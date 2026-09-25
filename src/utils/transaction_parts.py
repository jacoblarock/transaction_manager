from utils import db
from utils.auth import check_auth
from utils.logs import logger


def create_transaction_part(
    s_token: str,
    t_id: int,
    target_u_id: int,
    tp_amount: float,
) -> int:
    u_id = check_auth(s_token)
    logger.info(f"create transaction part user={u_id} transaction={t_id} target={target_u_id} amount={tp_amount}")
    with db.connect() as conn:
        transaction_rows = db.select(
            conn,
            f"select t_g_ref, t_amount from transactions where t_id = {t_id};"
        )
        if len(transaction_rows) == 0:
            return -1
        g_id = transaction_rows[0]["t_g_ref"]
        t_amount = float(transaction_rows[0]["t_amount"])
        membership_count = db.select(
            conn,
            f"select count(*) as row_count from user_group_map where ugm_u_ref = {u_id} and ugm_g_ref = {g_id};"
        )[0]["row_count"]
        if membership_count == 0:
            return -1
        existing_rows = db.select(
            conn,
            f"select coalesce(sum(tp_amount), 0) as total from transaction_parts where tp_t_ref = {t_id};"
        )
        existing_total = float(existing_rows[0]["total"])
        if existing_total + tp_amount > t_amount + 0.0001:
            return -2
        tp_id = db.insert(
            conn,
            "transaction_parts",
            [{
                "tp_t_ref": t_id,
                "tp_u_ref": target_u_id,
                "tp_amount": tp_amount,
            }],
            primary_key="tp_id",
        )[0]
        return tp_id


def delete_transaction_part(
    s_token: str,
    tp_id: int,
) -> bool:
    u_id = check_auth(s_token)
    logger.info(f"delete transaction part user={u_id} part={tp_id}")
    with db.connect() as conn:
        part_rows = db.select(
            conn,
            f"select tp_t_ref from transaction_parts where tp_id = {tp_id};"
        )
        if len(part_rows) == 0:
            return False
        t_id = part_rows[0]["tp_t_ref"]
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
            "transaction_parts",
            [{"tp_id": tp_id}],
        )
        return True


def update_transaction_part(
    s_token: str,
    tp_id: int,
    target_u_id: int,
    tp_amount: float,
) -> int | bool:
    u_id = check_auth(s_token)
    logger.info(f"update transaction part user={u_id} part={tp_id} target={target_u_id} amount={tp_amount}")
    with db.connect() as conn:
        part_rows = db.select(
            conn,
            f"select tp_t_ref from transaction_parts where tp_id = {tp_id};"
        )
        if len(part_rows) == 0:
            return False
        t_id = part_rows[0]["tp_t_ref"]
        transaction_rows = db.select(
            conn,
            f"select t_g_ref, t_amount from transactions where t_id = {t_id};"
        )
        if len(transaction_rows) == 0:
            return False
        g_id = transaction_rows[0]["t_g_ref"]
        t_amount = float(transaction_rows[0]["t_amount"])
        membership_count = db.select(
            conn,
            f"select count(*) as row_count from user_group_map where ugm_u_ref = {u_id} and ugm_g_ref = {g_id};"
        )[0]["row_count"]
        if membership_count == 0:
            return False
        existing_rows = db.select(
            conn,
            f"select coalesce(sum(tp_amount), 0) as total from transaction_parts where tp_t_ref = {t_id} and tp_id != {tp_id};"
        )
        existing_total = float(existing_rows[0]["total"])
        if existing_total + tp_amount > t_amount + 0.0001:
            return -2
        db.update(
            conn,
            "transaction_parts",
            {"tp_u_ref": target_u_id, "tp_amount": tp_amount},
            [{"tp_id": tp_id}],
        )
        return True


def get_transaction_parts(
    s_token: str,
    t_id: int,
) -> list[db.RealDictRow]:
    u_id = check_auth(s_token)
    logger.info(f"get transaction parts user={u_id} transaction={t_id}")
    with db.connect() as conn:
        transaction_rows = db.select(
            conn,
            f"select t_g_ref from transactions where t_id = {t_id};"
        )
        if len(transaction_rows) == 0:
            return []
        g_id = transaction_rows[0]["t_g_ref"]
        membership_count = db.select(
            conn,
            f"select count(*) as row_count from user_group_map where ugm_u_ref = {u_id} and ugm_g_ref = {g_id};"
        )[0]["row_count"]
        if membership_count == 0:
            return []
        return db.select(
            conn,
            "select tp_id, tp_t_ref, tp_u_ref, tp_amount, tp_created_at "
            f"from transaction_parts where tp_t_ref = {t_id};"
        )
