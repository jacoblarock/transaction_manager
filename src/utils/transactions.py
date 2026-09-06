from utils import db
from utils.auth import check_auth
from utils.logs import logger


def create_transaction(
    s_token: str,
    g_id: int,
    t_name: str,
    t_amount: float,
    t_date: str | None = None,
) -> int:
    u_id = check_auth(s_token)
    logger.info(f"create transaction user={u_id} group={g_id} name={t_name} amount={t_amount} date={t_date}")
    with db.connect() as conn:
        membership_count = db.select(
            conn,
            f"select count(*) as row_count from user_group_map where ugm_u_ref = {u_id} and ugm_g_ref = {g_id};"
        )[0]["row_count"]
        if membership_count == 0:
            return -1
        row = {
            "t_u_ref": u_id,
            "t_name": t_name,
            "t_g_ref": g_id,
            "t_amount": t_amount,
        }
        if t_date is not None:
            row["t_date"] = t_date
        t_id = db.insert(
            conn,
            "transactions",
            [row],
            primary_key="t_id",
        )[0]
        return t_id


def delete_transaction(
    s_token: str,
    t_id: int,
) -> bool:
    u_id = check_auth(s_token)
    logger.info(f"delete transaction user={u_id} transaction={t_id}")
    with db.connect() as conn:
        transaction_rows = db.select(
            conn,
            f"select t_g_ref from transactions where t_id = {t_id};"
        )
        if len(transaction_rows) == 0:
            return False
        g_id = transaction_rows[0]["t_g_ref"]
        membership_count = db.select(
            conn,
            f"select count(*) as row_count from user_group_map where ugm_u_ref = {u_id} and ugm_g_ref = {g_id};"
        )[0]["row_count"]
        if membership_count == 0:
            return False
        db.delete(
            conn,
            "transactions",
            [{"t_id": t_id}],
        )
        return True


def update_transaction(
    s_token: str,
    t_id: int,
    t_name: str,
    t_amount: float,
    t_date: str | None = None,
) -> bool:
    u_id = check_auth(s_token)
    logger.info(f"update transaction user={u_id} transaction={t_id} name={t_name} amount={t_amount} date={t_date}")
    with db.connect() as conn:
        transaction_rows = db.select(
            conn,
            f"select t_g_ref from transactions where t_id = {t_id};"
        )
        if len(transaction_rows) == 0:
            return False
        g_id = transaction_rows[0]["t_g_ref"]
        membership_count = db.select(
            conn,
            f"select count(*) as row_count from user_group_map where ugm_u_ref = {u_id} and ugm_g_ref = {g_id};"
        )[0]["row_count"]
        if membership_count == 0:
            return False
        to_update = {"t_name": t_name, "t_amount": t_amount}
        if t_date is not None:
            to_update["t_date"] = t_date
        db.update(
            conn,
            "transactions",
            to_update,
            [{"t_id": t_id}],
        )
        return True


def get_transactions(
    s_token: str,
    g_id: int,
) -> list[db.RealDictRow]:
    u_id = check_auth(s_token)
    logger.info(f"get transactions user={u_id} group={g_id}")
    with db.connect() as conn:
        membership_count = db.select(
            conn,
            f"select count(*) as row_count from user_group_map where ugm_u_ref = {u_id} and ugm_g_ref = {g_id};"
        )[0]["row_count"]
        if membership_count == 0:
            return []
        return db.select(
            conn,
            "select t_id, t_u_ref, t_name, t_g_ref, t_amount, t_date, t_created_at "
            f"from transactions where t_g_ref = {g_id};"
        )