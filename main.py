import os
import time

from flask import Flask, render_template, request, jsonify
from data import db_session
from data.users import User
from data.routes import Route
from maps_handler import Map

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
test_map = Map()
users_img_stack = {"admin": []}
users_maps = {"admin": Map()}


@app.route("/map")
def map():
    for img in users_img_stack["admin"]:
        os.remove(img)
    users_img_stack["admin"] = []
    users_maps["admin"] = Map()
    return render_template("map_creating.html", img="../static/img/starter_map.png")


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
