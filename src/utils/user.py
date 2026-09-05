from utils import db
from utils.auth import check_invite_token, gen_session_token
from utils.logs import logger
from datetime import datetime


def create_invite_token() -> str:
    logger.info("creating invite token")
    it_token = gen_session_token()
    with db.connect() as conn:
        db.insert(
            conn,
            "invite_tokens",
            [{
                "it_token": it_token
            }]
        )
    logger.info(f"created invite token {it_token}")
    return it_token


def create_user_with_token(it_token: str, u_name: str, pass_hash: str) -> tuple[str,int]:
    logger.info(f"attempting user creation name={u_name}")
    it_id = check_invite_token(it_token)
    if it_id < 0:
        logger.error("invalid invite token")
        return "invalid invite token", 400
    with db.connect() as conn:
        name_collision_rows = db.select(
            conn,
            f"select u_id from users where u_name = '{u_name}';"
        )
        if len(name_collision_rows) > 1:
            logger.error("user already exists")
            return "user with username already exists", 400
        logger.info("updating invite token")
        db.update(
            conn,
            "invite_tokens",
            {"it_expires": str(datetime.now())},
            [{"it_id": it_id}]
        )
        logger.info("creating user")
        db.insert(
            conn,
            "users",
            [{
                "u_name": u_name,
                "u_pass": pass_hash,
            }]
        )
        return "success", 200