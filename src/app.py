from flask import Flask, request
from migrations.migrate import migrate
from utils import auth

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


if __name__ == "__main__":
    from waitress import serve
    migrate()
    serve(app, host="0.0.0.0", port=8000)