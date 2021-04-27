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

    email = StringField('Email', [validators.Length(min=6, max=50),  # validators.Email(),
                                  validators.DataRequired()])

    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message="Passwords don't match")
    ])
    confirm = PasswordField('Confirm Password')


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
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
    if request.method == 'POST':
        username = request.form.get('username', False)
        password_check = request.form.get('password', False)
        password = ''

        con = sqlite3.connect('db/users.db')
        cur = con.cursor()

        result = cur.execute(f"""SELECT username, hashed_password FROM users""").fetchall()

        for res in result:
            if res[0] == username:
                password = res[1]

        if password == '':
            flash('Invalid username')

        elif check_password_hash(password, password_check):
            session['logged_in'] = True
            session['username'] = username

            flash('You are now logged in', 'success')

            # return redirect(url_for('register'))
        else:
            flash('Invalid password')

        cur.close()

    return render_template('login.html')


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login')
            return redirect(url_for('login'))

    return wrap


@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out')
    return redirect(url_for('login'))


@app.route("/map", methods=["POST", "GET"])
def map():
    if request.method == "GET":
        for img in users_img_stack["admin"]:
            os.remove(img)
        users_img_stack["admin"] = []
        users_maps["admin"] = Map()
        img_num = time.time_ns()
        cur_map = "static/img/users_maps/map-123-" + str(img_num)[4:] + ".png"
        users_maps["admin"].request_map(cur_map)
        return render_template("map_creating.html", img="../" + cur_map)
    elif request.method == "POST":
        return request.form["path_name"] + "\n" + users_maps["admin"].get_data_string()


@app.route("/_map", methods=["POST"])
def _map():
    req = request.form.get("req_type")
    if req == "place":
        mouse_x = request.form.get("mouse_x")
        mouse_y = request.form.get("mouse_y")
        users_maps["admin"].place_point(int(mouse_x) - 140, int(mouse_y) - 150)

    elif req == "move":
        direction = request.form.get("direction")
        directions = direction.split("-")  # Ведь есть направления типа "right-up"
        for d in directions:
            users_maps["admin"].move(d)

    elif req == "zoom":
        zoom_type = request.form.get("zoom_type")
        if zoom_type == "plus":
            users_maps["admin"].change_z(users_maps["admin"].z + 1)
        elif zoom_type == "minus":
            users_maps["admin"].change_z(users_maps["admin"].z - 1)
    elif req == "time_travel":
        travel_type = request.form.get("travel_type")
        if travel_type == "step_back":
            users_maps["admin"].undo()

    img_num = time.time_ns()
    cur_map = "static/img/users_maps/map-123-" + str(img_num)[4:] + ".png"
    users_maps["admin"].request_map(cur_map)
    if users_img_stack["admin"]:
        os.remove(users_img_stack["admin"].pop())
    users_img_stack["admin"].append(cur_map)
    return "../" + cur_map


def main():
    db_session.global_init("db/users.db")
    app.run(port=8888, host="127.0.0.1")


if __name__ == '__main__':
    main()
