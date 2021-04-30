import os
import time

from flask import Flask, render_template, flash, redirect, url_for, session, request, logging, \
    jsonify
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
from data import db_session
from data.users import User
from data.routes import Route
from maps_handler import Map

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
test_map = Map()
users_img_stack = {"admin": []}
users_maps = {"admin": Map()}


class RegisterForm(Form):
    username = StringField('Username',
                           [validators.Length(min=3, max=15), validators.DataRequired()])

    email = StringField('Email',
                        [validators.Length(min=6, max=50), validators.Email(),
                         validators.DataRequired()])

    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message="Passwords don't match")
    ])
    confirm = PasswordField('Confirm Password')


@app.route('/')
def index():
    """Главная страница"""
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Страница регистрации"""
    form = RegisterForm(request.form)

    if request.method == 'POST' and form.validate():
        email = form.email.data
        username = form.username.data
        password = generate_password_hash(str(form.password.data))

        con = sqlite3.connect('db/users.db')
        cur = con.cursor()

        results = cur.execute("SELECT username, email FROM users").fetchall()

        for res in results:
            if res[0] == str(username) or res[1] == email:
                if res[0] == str(username):
                    flash('Username is already taken')

                    error = 'Username is already taken'
                    return render_template('register.html', error=error, form=form)

                elif res[1] == email:
                    flash('This email is already registered')

                    error = 'This email is already registered'
                    return render_template('register.html', error=error, form=form)

        cur.execute("INSERT INTO users(email, username, hashed_password) VALUES(?, ?, ?);",
                    (email, username, password))

        con.commit()
        con.close()

        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа"""
    if request.method == 'POST':
        username = request.form.get('username', False)
        password_check = request.form.get('password', False)
        password = ''

        con = sqlite3.connect('db/users.db')
        cur = con.cursor()

        result = cur.execute(f"""SELECT username, hashed_password, id FROM users""").fetchall()

        for res in result:
            if res[0] == username:
                password = res[1]
                uid = res[2]

        if password == '':
            flash('Invalid username')

        elif check_password_hash(password, password_check):
            session['logged_in'] = True
            session['username'] = username
            session["img_stack"] = []
            users_maps[session["username"]] = Map()
            session['id'] = uid
            session.pop('_flashes', None)
            flash('You are now logged in', 'success')

            return redirect("/")
        else:
            session.pop('_flashes', None)
            flash('Invalid password')

        cur.close()

    return render_template('login.html')


def is_logged_in(f):
    """Проверяет, вошел ли пользователь"""

    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            session.pop('_flashes', None)
            flash('Unauthorized, Please log in')
            return redirect(url_for('login'))

    return wrap


@app.route('/logout')
@is_logged_in
def logout():
    """Функция для выхода"""
    for img in session['img_stack']:
        if os.path.exists(img):
            os.remove(img)
    session.clear()
    flash('You are now logged out')
    return redirect(url_for('login'))


@app.route("/map", methods=["POST", "GET"])
@is_logged_in
def map():
    """Страница для создания нового пути"""
    if request.method == "GET":
        for img in session["img_stack"]:
            if os.path.exists(img):
                os.remove(img)
        session["img_stack"] = []
        users_maps[session["username"]] = Map()
        img_num = time.time_ns()
        cur_map = f"static/img/users_maps/map-{session['id']}-{str(img_num)[4:]}.png"
        users_maps[session["username"]].request_map(cur_map)
        session['img_stack'].append(cur_map)
        return render_template("map_creating.html", img="../" + cur_map)
    elif request.method == "POST":
        db_sess = db_session.create_session()
        new_route = Route()
        if request.form['path_name']:
            new_route.name = request.form["path_name"]
        else:
            new_route.name = 'Unnamed path'
        new_route.points = users_maps[session["username"]].get_data_string()
        new_route.user_id = session["id"]
        db_sess.add(new_route)
        db_sess.commit()
        return redirect("paths")


@app.route("/_map", methods=["POST"])
def _map():
    """Обработчик ajax запросов со страниц с картой (которая map() и spectate_map())"""
    req = request.form.get("req_type")
    if req == "place":
        mouse_x = request.form.get("mouse_x")
        mouse_y = request.form.get("mouse_y")
        users_maps[session["username"]].place_point(int(mouse_x) - 140, int(mouse_y) - 150)

    elif req == "move":
        direction = request.form.get("direction")
        directions = direction.split("-")  # Ведь есть направления типа "right-up"
        for d in directions:
            users_maps[session["username"]].move(d)

    elif req == "zoom":
        zoom_type = request.form.get("zoom_type")
        if zoom_type == "plus":
            users_maps[session["username"]].change_z(users_maps[session["username"]].z + 1)
        elif zoom_type == "minus":
            users_maps[session["username"]].change_z(users_maps[session["username"]].z - 1)
    elif req == "time_travel":
        travel_type = request.form.get("travel_type")
        if travel_type == "step_back":
            users_maps[session["username"]].undo()

    img_num = time.time_ns()
    cur_map = f"static/img/users_maps/map-{session['id']}-{str(img_num)[4:]}.png"
    users_maps[session["username"]].request_map(cur_map)
    for img in session["img_stack"]:
        if os.path.exists(img):
            os.remove(img)
    session['img_stack'] = [cur_map]
    return "../" + cur_map


@app.route("/map/<int:path_id>")
@is_logged_in
def spectate_map(path_id):
    """Страница для просмотра уже созданных путей"""
    if request.method == "GET":
        db_sess = db_session.create_session()
        the_route = db_sess.query(Route).filter(Route.id == path_id).first()
        if the_route:
            if the_route.user_id != session['id']:
                return render_template("bad_page.html", message="That's not your path!")
        else:
            return render_template("bad_page.html", message="This path does not exist")
        for img in session['img_stack']:
            if os.path.exists(img):
                os.remove(img)
        session['img_stack'] = []
        users_maps[session["username"]] = Map(data_string=the_route.points)
        img_num = time.time_ns()
        cur_map = f"static/img/users_maps/map-{session['id']}-{str(img_num)[4:]}.png"
        users_maps[session["username"]].request_map(cur_map)
        session['img_stack'].append(cur_map)
        return render_template("map_spectating.html", img="../" + cur_map)


@app.route("/paths", methods=["POST", "GET"])
@is_logged_in
def map_browser():
    """Страница со всеми путями пользователя"""
    if request.method == "GET":
        db_sess = db_session.create_session()
        uid = db_sess.query(User).filter(User.username == session["username"]).first()
        uid = uid.id
        paths = db_sess.query(Route).filter(Route.user_id == uid)
        params = {"paths": []}
        for path in paths:
            params["paths"].append({"id": path.id, "name": path.name})
        return render_template("map_browser.html", **params)
    else:
        db_sess = db_session.create_session()
        bad_route = db_sess.query(Route).filter(Route.id == request.form["data"]).first()
        db_sess.delete(bad_route)
        db_sess.commit()
        return redirect("paths")


@app.errorhandler(404)
def not_found(*args):
    """Красивая страница 404"""
    return render_template("bad_page.html", message="404: This page does not exist")


def main():
    if not os.path.exists("static/img/users_maps"):
        os.mkdir("static/img/users_maps")
    if not os.path.exists("db"):
        os.mkdir("db")
    db_session.global_init("db/users.db")
    app.run(port=8888, host="127.0.0.1")


if __name__ == '__main__':
    main()
