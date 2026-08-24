from flask import Flask
from migrations.migrate import migrate
from utils.logs import logger

app = Flask(__name__)


@app.route("/")
def hello():
    return "hello world!", 200


if __name__ == "__main__":
    from waitress import serve
    migrate()
    serve(app, host="0.0.0.0", port=8000)