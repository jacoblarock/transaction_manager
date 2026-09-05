from flask import Flask, request
from migrations.migrate import migrate
from utils import auth
from utils import user
from utils import groups

app = Flask(__name__)



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


@app.route("/api/create_user_from_invite_token", methods=["GET"])
def create_user_from_invite_token() -> tuple[str,int]:
    it_token = request.args.get("token")
    u_name = request.args.get("user")
    pass_hash = request.args.get("passHash")
    if type(it_token) == str and type(u_name) == str and type(pass_hash) == str:
        return user.create_user_with_token(it_token, u_name, pass_hash)
    return "invalid request format", 400


@app.route("/api/get_groups", methods=["GET"])
def get_groups() -> tuple[str, int]:
    s_token = request.args.get("token")
    if not s_token:
        return "no token provided", 400
    rows = groups.get_groups(s_token)
    return rows, 200


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
    u_id = request.args.get("userId")
    g_id = request.args.get("groupId")
    if type(s_token) == str and type(u_id) == str and type(g_id) == str:
        try:
            u_id_int = int(u_id)
            g_id_int = int(g_id)
        except ValueError:
            return "invalid id", 400
        result = groups.add_user_to_group(u_id_int, g_id_int)
        if result == -1:
            return "user already in group", 400
        return str(result), 200
    return "invalid request format", 400


@app.route("/api/remove_user_from_group", methods=["GET"])
def remove_user_from_group() -> tuple[str, int]:
    s_token = request.args.get("token")
    u_id = request.args.get("userId")
    g_id = request.args.get("groupId")
    if type(u_id) == str and type(g_id) == str:
        try:
            u_id_int = int(u_id)
            g_id_int = int(g_id)
        except ValueError:
            return "invalid id", 400
        result = groups.remove_user_from_group(u_id_int, g_id_int)
        if result == -1:
            return "user not in group", 400
        return "success", 200
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