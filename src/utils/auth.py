from random import choices
from string import ascii_uppercase, digits
from datetime import datetime
from utils import db
from utils.logs import logger


def gen_session_token() -> str:
    return ''.join(choices(ascii_uppercase + digits, k=100))


def check_auth(s_token: str) -> int:
    with db.connect() as conn:
        session_rows = db.select(
            conn,
            f"select s_u_ref from sessions where s_token = '{s_token}' and s_expires > '{datetime.now()}';"
        )
        if len(session_rows) != 1:
            logger.error("no active session found")
            return -1
        u_id = session_rows[0].get("s_u_ref")
        if u_id:
            logger.info(f"session found for user {u_id}")
            return u_id
        return -1


def authenticate(u_name: str, pass_hash: str) -> tuple[str,int]:
    with db.connect() as conn:
        u_id_rows = db.select(
            conn,
            f"select u_id from users where u_name = '{u_name}';"
        )
        if len(u_id_rows) != 1:
            return "user not found", 400
        u_id = u_id_rows[0].get("u_id")
        logger.info(f"Attempting auth for user {u_name} id={u_id}")
        u_pass = db.select(
            conn,
            f"select u_pass from users where u_id = {u_id};"
        )[0]["u_pass"]
        logger.info(f"db={u_pass}, arg={pass_hash}")
        if u_pass == pass_hash:
            s_token = gen_session_token()
            db.insert(
                conn,
                "sessions",
                [{
                    "s_u_ref": u_id,
                    "s_token": s_token,
                }],
            )
            return s_token, 200
        else:
            return "password does not match", 400