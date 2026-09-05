from utils import db
from utils.auth import check_auth
from utils.logs import logger


def settle_balances(s_token: str, g_id: int) -> list[dict]:
    u_id = check_auth(s_token)
    logger.info(f"settle balances user={u_id} group={g_id}")
    with db.connect() as conn:
        membership_count = db.select(
            conn,
            f"select count(*) as row_count from user_group_map where ugm_u_ref = {u_id} and ugm_g_ref = {g_id};"
        )[0]["row_count"]
        if membership_count == 0:
            return []

        member_rows = db.select(
            conn,
            f"select ugm_u_ref from user_group_map where ugm_g_ref = {g_id};"
        )
        user_ids = [row["ugm_u_ref"] for row in member_rows]
        n = len(user_ids)
        if n == 0:
            return []

        balances = {uid: 0.0 for uid in user_ids}

        transaction_rows = db.select(
            conn,
            f"select t_u_ref, t_amount from transactions where t_g_ref = {g_id};"
        )
        total = 0.0
        for row in transaction_rows:
            amount = float(row["t_amount"])
            balances[row["t_u_ref"]] += amount
            total += amount
        share = total / n
        for uid in user_ids:
            balances[uid] -= share

        payment_rows = db.select(
            conn,
            f"select p_u_sender, p_u_recipient, p_amount from payments where p_g_ref = {g_id};"
        )
        for row in payment_rows:
            amount = float(row["p_amount"])
            balances[row["p_u_sender"]] += amount
            balances[row["p_u_recipient"]] -= amount

        debtors = sorted(
            [(uid, -bal) for uid, bal in balances.items() if bal < -0.01],
            key=lambda x: x[1],
            reverse=True,
        )
        creditors = sorted(
            [(uid, bal) for uid, bal in balances.items() if bal > 0.01],
            key=lambda x: x[1],
            reverse=True,
        )

        result = []
        i = j = 0
        while i < len(debtors) and j < len(creditors):
            d_uid, d_amt = debtors[i]
            c_uid, c_amt = creditors[j]
            transfer = min(d_amt, c_amt)
            result.append({"from": d_uid, "to": c_uid, "amount": round(transfer, 2)})
            debtors[i] = (d_uid, d_amt - transfer)
            creditors[j] = (c_uid, c_amt - transfer)
            if debtors[i][1] < 0.01:
                i += 1
            if creditors[j][1] < 0.01:
                j += 1

        return result
