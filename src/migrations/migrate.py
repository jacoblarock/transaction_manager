import os
from utils import db
from utils.logs import logger

def migrate():
    with db.connect() as conn:
        migration_exists = db.select(
            conn,
            "select count(*) as count from information_schema.tables where table_name = 'migrations';"
        )[0]["count"] > 0
        if not migration_exists:
            with open("migrations/_migrations.sql") as file:
                db.execute(conn, file.read())
            logger.info("created migrations table")
        complete_migrations = [row["m_name"] for row in db.select(
            conn,
            "select m_name from migrations;"
        )]
        for path in os.listdir("migrations/"):
            if (
                ".sql" not in path 
                or path == "_migrations.sql"
                or path in complete_migrations
            ):
                continue
            with open(f"migrations/{path}") as file:
                logger.info(f"performing migration {path}")
                db.execute(conn, file.read())
                db.insert(
                    conn,
                    "migrations",
                    [{
                        "m_name": path,
                    }]
                )
                logger.info(f"completed migration {path}")