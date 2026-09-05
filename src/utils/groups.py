from utils import db
from utils.auth import check_auth
from utils.logs import logger


def get_groups(s_token: str) -> list[db.RealDictRow]:
    u_id = check_auth(s_token)
    logger.info(f"get groups for user {u_id}")
    with db.connect() as conn:
        return db.select(
            conn,
            "select g_id, g_name "
            "from groups join user_group_map on ugm_g_ref = g_id "
            f"where ugm_u_ref = {u_id};"
        )


def add_user_to_group(s_token: str, target_u_id: int, g_id: int) -> int:
    u_id = check_auth(s_token)
    logger.info(f"add user {target_u_id} to group {g_id} by user {u_id}")
    with db.connect() as conn:
        caller_row_count = db.select(
            conn,
            f"select count(*) as row_count from user_group_map where ugm_u_ref = {u_id} and ugm_g_ref = {g_id};"
        )[0]["row_count"]
        if caller_row_count == 0:
            return -1
        existing_row_count = db.select(
            conn,
            f"select count(*) as row_count from user_group_map where ugm_u_ref = {target_u_id} and ugm_g_ref = {g_id};"
        )[0]["row_count"]
        if existing_row_count > 0:
            return -2
        ugm_id = db.insert(
            conn,
            "user_group_map",
            [{
                "ugm_u_ref": target_u_id,
                "ugm_g_ref": g_id,
            }],
            primary_key="ugm_id"
        )[0]
        return ugm_id
        

def remove_user_from_group(s_token: str, target_u_id: int, g_id: int) -> int:
    u_id = check_auth(s_token)
    logger.info(f"remove user {target_u_id} from group {g_id} by user {u_id}")
    with db.connect() as conn:
        caller_row_count = db.select(
            conn,
            f"select count(*) as row_count from user_group_map where ugm_u_ref = {u_id} and ugm_g_ref = {g_id};"
        )[0]["row_count"]
        if caller_row_count == 0:
            return -1
        existing_row_count = db.select(
            conn,
            f"select count(*) as row_count from user_group_map where ugm_u_ref = {target_u_id} and ugm_g_ref = {g_id};"
        )[0]["row_count"]
        if existing_row_count == 0:
            return -2
        return db.delete(
            conn,
            "user_group_map",
            [{
                "ugm_u_ref": target_u_id,
                "ugm_g_ref": g_id,
            }],
        )


def create_group(s_token: str, g_name: str) -> int:
    u_id = check_auth(s_token)
    logger.info(f"create group user={u_id} name={g_name}")
    with db.connect() as conn:
        g_id = db.insert(
            conn,
            "groups",
            [{
                "g_name": g_name
            }],
            primary_key="g_id",
        )[0]
        db.insert(
            conn,
            "user_group_map",
            [{
                "ugm_u_ref": u_id,
                "ugm_g_ref": g_id,
            }],
            primary_key="ugm_id",
        )
        return g_id


def delete_group(s_token: str, g_id: int) -> bool:
    u_id = check_auth(s_token)
    logger.info(f"delete group user={u_id} group={g_id}")
    with db.connect() as conn:
        membership_count = db.select(
            conn,
            f"select count(*) as row_count from user_group_map where ugm_u_ref = {u_id} and ugm_g_ref = {g_id};"
        )[0]["row_count"]
        if membership_count == 0:
            return False
        db.delete(
            conn,
            "user_group_map",
            [{"ugm_g_ref": g_id}],
        )
        db.delete(
            conn,
            "groups",
            [{"g_id": g_id}],
        )
        return True