from flask import Flask, render_template
from data import db_session
from data.users import User
from data.routes import Route

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route("/index")
def index():
    param = {"img": "../static/img/map.png"}
    return render_template("map_creating.html", **param)


def main():
    db_session.global_init("db/users.db")
    app.run(port=8888, host="127.0.0.1")


if __name__ == '__main__':
    main()
