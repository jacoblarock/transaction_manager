from flask import Flask, request, send_from_directory
from migrations.migrate import migrate
from utils import auth
from utils import user
from utils import groups
from utils import transactions
from utils import payments
from utils import settlement
import os

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), "static"), static_url_path="/static")



@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/")
def healthcheck() -> tuple[str,int]:
    return "healthcheck", 200


@app.route("/api/authenticate", methods=["GET"])
def authenticate() -> tuple[str,int]:
    u_name = request.args.get("user")
    pass_hash = request.args.get("passHash")
    if type(u_name) == str and type(pass_hash) == str:
        return auth.authenticate(u_name, pass_hash)
    return "invalid request format", 400


@app.route("/api/auth_check", methods=["GET"])
def auth_check() -> tuple[str,int]:
    s_token = request.args.get("token")
    if not s_token:
        return "no token provided", 400
    if auth.check_auth(s_token) > 0:
        return "success", 200
    return "session not found", 400


@app.route("/api/create_invite_token", methods=["GET"])
def create_invite_token() -> tuple[str, int]:
    s_token = request.args.get("token")
    if not s_token:
        return "no token provided", 400
    if auth.check_auth(s_token) < 0:
        return "invalid token", 400
    return user.create_invite_token(), 200


@app.route("/api/get_user_id", methods=["GET"])
def get_user_id() -> tuple[str, int]:
    s_token = request.args.get("token")
    u_name = request.args.get("user")
    if type(s_token) == str and type(u_name) == str:
        result = user.get_user_id(s_token, u_name)
        if result < 0:
            return "user not found", 400
        return str(result), 200
    return "invalid request format", 400


@app.route("/api/create_user_from_invite_token", methods=["GET"])
def create_user_from_invite_token() -> tuple[str,int]:
    it_token = request.args.get("token")
    u_name = request.args.get("user")
    pass_hash = request.args.get("passHash")
    if type(it_token) == str and type(u_name) == str and type(pass_hash) == str:
        return user.create_user_with_token(it_token, u_name, pass_hash)
    return "invalid request format", 400


@app.route("/api/get_groups", methods=["GET"])
def get_groups() -> tuple[list | str, int]:
    s_token = request.args.get("token")
    if not s_token:
        return "no token provided", 400
    rows = groups.get_groups(s_token)
    return rows, 200


@app.route("/api/get_group_users", methods=["GET"])
def get_group_users() -> tuple[list | str, int]:
    s_token = request.args.get("token")
    g_id = request.args.get("groupId")
    if type(s_token) == str and type(g_id) == str:
        try:
            g_id_int = int(g_id)
        except ValueError:
            return "invalid id", 400
        rows = groups.get_group_users(s_token, g_id_int)
        return rows, 200
    return "invalid request format", 400


@app.route("/api/create_group", methods=["GET"])
def create_group() -> tuple[str, int]:
    s_token = request.args.get("token")
    g_name = request.args.get("name")
    if type(s_token) == str and type(g_name) == str:
        return str(groups.create_group(s_token, g_name)), 200
    return "invalid request format", 400


@app.route("/api/delete_group", methods=["GET"])
def delete_group() -> tuple[str, int]:
    s_token = request.args.get("token")
    g_id = request.args.get("groupId")
    if type(s_token) == str and type(g_id) == str:
        try:
            g_id_int = int(g_id)
        except ValueError:
            return "invalid group id", 400
        if not groups.delete_group(s_token, g_id_int):
            return "user not in group", 403
        return "success", 200
    return "invalid request format", 400


@app.route("/api/add_user_to_group", methods=["GET"])
def add_user_to_group() -> tuple[str, int]:
    s_token = request.args.get("token")
    if not s_token:
        return "invalid request format", 400
    if auth.check_auth(s_token) < 0:
        return "invalid token", 400
    u_id = request.args.get("userId")
    g_id = request.args.get("groupId")
    if type(s_token) == str and type(u_id) == str and type(g_id) == str:
        try:
            u_id_int = int(u_id)
            g_id_int = int(g_id)
        except ValueError:
            return "invalid id", 400
        result = groups.add_user_to_group(s_token, u_id_int, g_id_int)
        if result == -1:
            return "calling user not in group", 403
        if result == -2:
            return "user already in group", 400
        return str(result), 200
    return "invalid request format", 400


@app.route("/api/remove_user_from_group", methods=["GET"])
def remove_user_from_group() -> tuple[str, int]:
    s_token = request.args.get("token")
    if not s_token:
        return "invalid request format", 400
    if auth.check_auth(s_token) < 0:
        return "invalid token", 400
    u_id = request.args.get("userId")
    g_id = request.args.get("groupId")
    if type(u_id) == str and type(g_id) == str:
        try:
            u_id_int = int(u_id)
            g_id_int = int(g_id)
        except ValueError:
            return "invalid id", 400
        result = groups.remove_user_from_group(s_token, u_id_int, g_id_int)
        if result == -1:
            return "calling user not in group", 403
        if result == -2:
            return "user not in group", 400
        return "success", 200
    return "invalid request format", 400


@app.route("/api/create_transaction", methods=["GET"])
def create_transaction() -> tuple[str, int]:
    s_token = request.args.get("token")
    g_id = request.args.get("groupId")
    t_name = request.args.get("name")
    t_amount = request.args.get("amount")
    t_date = request.args.get("date")
    if type(s_token) == str and type(g_id) == str and type(t_name) == str and type(t_amount) == str:
        try:
            g_id_int = int(g_id)
            t_amount_float = float(t_amount)
        except ValueError:
            return "invalid id", 400
        result = transactions.create_transaction(s_token, g_id_int, t_name, t_amount_float, t_date)
        if result == -1:
            return "user not in group", 403
        return str(result), 200
    return "invalid request format", 400


@app.route("/api/delete_transaction", methods=["GET"])
def delete_transaction() -> tuple[str, int]:
    s_token = request.args.get("token")
    t_id = request.args.get("transactionId")
    if type(s_token) == str and type(t_id) == str:
        try:
            t_id_int = int(t_id)
        except ValueError:
            return "invalid id", 400
        if not transactions.delete_transaction(s_token, t_id_int):
            return "user not in group", 403
        return "success", 200
    return "invalid request format", 400


@app.route("/api/update_transaction", methods=["GET"])
def update_transaction() -> tuple[str, int]:
    s_token = request.args.get("token")
    t_id = request.args.get("transactionId")
    t_name = request.args.get("name")
    t_amount = request.args.get("amount")
    t_date = request.args.get("date")
    if type(s_token) == str and type(t_id) == str and type(t_name) == str and type(t_amount) == str:
        try:
            t_id_int = int(t_id)
            t_amount_float = float(t_amount)
        except ValueError:
            return "invalid id", 400
        if not transactions.update_transaction(s_token, t_id_int, t_name, t_amount_float, t_date):
            return "user not in group", 403
        return "success", 200
    return "invalid request format", 400


@app.route("/api/get_transactions", methods=["GET"])
def get_transactions() -> tuple[list | str, int]:
    s_token = request.args.get("token")
    g_id = request.args.get("groupId")
    if type(s_token) == str and type(g_id) == str:
        try:
            g_id_int = int(g_id)
        except ValueError:
            return "invalid id", 400
        rows = transactions.get_transactions(s_token, g_id_int)
        return rows, 200
    return "invalid request format", 400


@app.route("/api/create_payment", methods=["GET"])
def create_payment() -> tuple[str, int]:
    s_token = request.args.get("token")
    g_id = request.args.get("groupId")
    recipient_u_id = request.args.get("recipientId")
    p_amount = request.args.get("amount")
    p_date = request.args.get("date")
    if type(s_token) == str and type(g_id) == str and type(recipient_u_id) == str and type(p_amount) == str:
        try:
            g_id_int = int(g_id)
            recipient_u_id_int = int(recipient_u_id)
            p_amount_float = float(p_amount)
        except ValueError:
            return "invalid id", 400
        result = payments.create_payment(s_token, g_id_int, recipient_u_id_int, p_amount_float, p_date)
        if result == -1:
            return "user not in group", 403
        return str(result), 200
    return "invalid request format", 400


@app.route("/api/delete_payment", methods=["GET"])
def delete_payment() -> tuple[str, int]:
    s_token = request.args.get("token")
    p_id = request.args.get("paymentId")
    if type(s_token) == str and type(p_id) == str:
        try:
            p_id_int = int(p_id)
        except ValueError:
            return "invalid id", 400
        if not payments.delete_payment(s_token, p_id_int):
            return "user not in group", 403
        return "success", 200
    return "invalid request format", 400


@app.route("/api/update_payment", methods=["GET"])
def update_payment() -> tuple[str, int]:
    s_token = request.args.get("token")
    p_id = request.args.get("paymentId")
    p_amount = request.args.get("amount")
    p_date = request.args.get("date")
    if type(s_token) == str and type(p_id) == str and type(p_amount) == str:
        try:
            p_id_int = int(p_id)
            p_amount_float = float(p_amount)
        except ValueError:
            return "invalid id", 400
        if not payments.update_payment(s_token, p_id_int, p_amount_float, p_date):
            return "user not in group", 403
        return "success", 200
    return "invalid request format", 400


@app.route("/api/get_payments", methods=["GET"])
def get_payments() -> tuple[list | str, int]:
    s_token = request.args.get("token")
    g_id = request.args.get("groupId")
    if type(s_token) == str and type(g_id) == str:
        try:
            g_id_int = int(g_id)
        except ValueError:
            return "invalid id", 400
        rows = payments.get_payments(s_token, g_id_int)
        return rows, 200
    return "invalid request format", 400


@app.route("/api/settle", methods=["GET"])
def settle() -> tuple[list | str, int]:
    s_token = request.args.get("token")
    g_id = request.args.get("groupId")
    if type(s_token) == str and type(g_id) == str:
        try:
            g_id_int = int(g_id)
        except ValueError:
            return "invalid id", 400
        rows = settlement.settle_balances(s_token, g_id_int)
        return rows, 200
    return "invalid request format", 400


if __name__ == "__main__":
    from waitress import serve
    from utils import db
    migrate()
    with db.connect() as conn:
        user_count = db.select(conn, "select count(*) as row_count from users;")[0]["row_count"]
    if user_count == 0:
        user.create_invite_token()
    serve(app, host="0.0.0.0", port=8000)