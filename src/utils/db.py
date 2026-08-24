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