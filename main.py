from flask import Flask, render_template, request, jsonify
from data import db_session
from data.users import User
from data.routes import Route

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route("/index")
def index():
    param = {"img": "../static/img/map.png"}
    return render_template("map_creating.html", **param)


@app.route("/map")
def map():
    return render_template("map_creating.html", img="../static/img/map.png")


@app.route("/_map", methods=["POST"])
def _map():
    mouse_x = request.form.get("mouse_x")
    mouse_y = request.form.get("mouse_y")
    print(mouse_x)
    print(mouse_y)
    return "../static/img/right_arrow.png"


def main():
    db_session.global_init("db/users.db")
    app.run(port=8888, host="127.0.0.1")


if __name__ == '__main__':
    main()
