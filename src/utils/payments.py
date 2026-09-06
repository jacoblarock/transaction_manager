from utils import db
from utils.auth import check_auth
from utils.logs import logger


def create_payment(
    s_token: str,
    g_id: int,
    recipient_u_id: int,
    p_amount: float,
    p_date: str | None = None,
) -> int:
    u_id = check_auth(s_token)
    logger.info(f"create payment user={u_id} group={g_id} recipient={recipient_u_id} amount={p_amount} date={p_date}")
    with db.connect() as conn:
        membership_count = db.select(
            conn,
            f"select count(*) as row_count from user_group_map where ugm_u_ref = {u_id} and ugm_g_ref = {g_id};"
        )[0]["row_count"]
        if membership_count == 0:
            return -1
        row = {
            "p_u_sender": u_id,
            "p_u_recipient": recipient_u_id,
            "p_g_ref": g_id,
            "p_amount": p_amount,
        }
        if p_date is not None:
            row["p_date"] = p_date
        p_id = db.insert(
            conn,
            "payments",
            [row],
            primary_key="p_id",
        )[0]
        return p_id


def delete_payment(
    s_token: str,
    p_id: int,
) -> bool:
    u_id = check_auth(s_token)
    logger.info(f"delete payment user={u_id} payment={p_id}")
    with db.connect() as conn:
        payment_rows = db.select(
            conn,
            f"select p_g_ref, p_u_sender from payments where p_id = {p_id};"
        )
        if len(payment_rows) == 0:
            return False
        g_id = payment_rows[0]["p_g_ref"]
        membership_count = db.select(
            conn,
            f"select count(*) as row_count from user_group_map where ugm_u_ref = {u_id} and ugm_g_ref = {g_id};"
        )[0]["row_count"]
        if membership_count == 0:
            return False
        db.delete(
            conn,
            "payments",
            [{"p_id": p_id}],
        )
        return True


def update_payment(
    s_token: str,
    p_id: int,
    p_amount: float,
    p_date: str | None = None,
) -> bool:
    u_id = check_auth(s_token)
    logger.info(f"update payment user={u_id} payment={p_id} amount={p_amount} date={p_date}")
    with db.connect() as conn:
        payment_rows = db.select(
            conn,
            f"select p_g_ref from payments where p_id = {p_id};"
        )
        if len(payment_rows) == 0:
            return False
        g_id = payment_rows[0]["p_g_ref"]
        membership_count = db.select(
            conn,
            f"select count(*) as row_count from user_group_map where ugm_u_ref = {u_id} and ugm_g_ref = {g_id};"
        )[0]["row_count"]
        if membership_count == 0:
            return False
        to_update = {"p_amount": p_amount}
        if p_date is not None:
            to_update["p_date"] = p_date
        db.update(
            conn,
            "payments",
            to_update,
            [{"p_id": p_id}],
        )
        return True


def get_payments(
    s_token: str,
    g_id: int,
) -> list[db.RealDictRow]:
    u_id = check_auth(s_token)
    logger.info(f"get payments user={u_id} group={g_id}")
    with db.connect() as conn:
        membership_count = db.select(
            conn,
            f"select count(*) as row_count from user_group_map where ugm_u_ref = {u_id} and ugm_g_ref = {g_id};"
        )[0]["row_count"]
        if membership_count == 0:
            return []
        return db.select(
            conn,
            "select p_id, p_u_sender, p_u_recipient, p_g_ref, p_amount, p_date, p_created_at "
            f"from payments where p_g_ref = {g_id};"
        )
