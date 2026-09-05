import psycopg2
from psycopg2.extensions import connection as PgConnection
from psycopg2.extras import RealDictCursor, RealDictRow, execute_batch
import os


def connect() -> PgConnection:
    password = os.environ.get("DB_PASSWORD")
    if password is None:
        raise EnvironmentError(
            "DB_PASSWORD environment variable is not set."
        )
    connection = psycopg2.connect(
        host="db",                # Docker container name
        port=5432,
        dbname="transaction_manager",
        user=os.environ.get("DB_USER", "postgres"),
        password=password,
        cursor_factory=RealDictCursor,
    )
    return connection


def execute(conn: PgConnection, query: str) -> int:
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.rowcount


def select(conn: PgConnection, query: str) -> list[RealDictRow]:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query)
        return cur.fetchall()


def insert(conn: PgConnection, table_name: str, rows: list[dict]) -> int:
    if not rows:
        return 0
    cols = list(rows[0].keys())
    query = (
        f"INSERT INTO {table_name} ({', '.join(cols)}) "
        f"VALUES ({', '.join(['%s'] * len(cols))})"
    )
    values = [tuple(row[col] for col in cols) for row in rows]
    with conn.cursor() as cur:
        execute_batch(cur, query, values)
        return cur.rowcount


def update(conn: PgConnection, table_name: str, to_update: dict, where: list[dict]) -> int:
    if not where:
        return 0
    set_clause = ", ".join(f"{col} = %s" for col in to_update)
    where_cols = list(where[0].keys())
    where_clause = " AND ".join(f"{col} = %s" for col in where_cols)
    query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
    set_values = [to_update[col] for col in to_update]
    values = [tuple(set_values + [row[col] for col in where_cols]) for row in where]
    with conn.cursor() as cur:
        execute_batch(cur, query, values)
        return cur.rowcount


def delete(conn: PgConnection, table_name: str, rows: list[dict]) -> int:
    if not rows:
        return 0
    cols = list(rows[0].keys())
    where_clause = " AND ".join(f"{col} = %s" for col in cols)
    query = f"DELETE FROM {table_name} WHERE {where_clause}"
    values = [tuple(row[col] for col in cols) for row in rows]
    with conn.cursor() as cur:
        execute_batch(cur, query, values)
        return cur.rowcount