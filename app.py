from flask import Flask, render_template, url_for, send_from_directory, request
from domain.application import Application
from domain.model import Model
from util import parse_json, pictures
import os
from werkzeug.utils import secure_filename
import app_functions

import random

app = Flask(__name__)
CONFIG_PATH = "config.json"
CONFIG = {}
applications = {}

@app.route('/')
def index():
    return render_template("index.html", title = "index", menu = get_menu_items("Home"), applications = get_apps_overview())

@app.route('/<app_name>')
def application(app_name):
    appNames = get_menu_items(app_name)
    if app_name in applications:
        modelsList, restriction = get_models_by_app(app_name)
        return render_template("application.html", compare = restriction, title = applications[app_name].name, app = app_name, menu = appNames, models = modelsList, pictures = pictures.random_pictures(CONFIG["number_of_pictures_to_show"], CONFIG["random_picture_list"]))
    else:
       return render_template("404.html", menu = appNames), 404 

@app.route('/<app_name>/output', methods=['POST'])
def output(app_name):

    # Menu generation
    appNames = get_menu_items(app_name)

    # Form data
    data = request.form

    method = data["method"]
    # case where nothing is selected
    if "non-selected" == method:
        return render_template("wrongOutput.html", menu = appNames, title = applications[app_name].name, info= "Did you select a picture?")
    # File uploaded by a user
    elif "user-file" == method:
        return app_functions.user_file_input(appNames, app_name, data, applications, CONFIG)
    # Random picture
    elif "random-picture" == method:
        return app_functions.random_picture_input(appNames, app_name, data, applications, CONFIG)

    return render_template("wrongOutput.html", menu = appNames, title = applications[app_name].name, info= "Unexpected error")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", title = "404", menu = get_menu_items("")), 404

def get_menu_items(selected_item):
    menu_items = [["", "Home", False]]
    if selected_item == "Home":
        menu_items[0][2] = True
    for i in applications.keys():
        menu_items.append([i, applications[i].name, False])
        if i == selected_item:
            menu_items[-1][2] = True
    return menu_items

def get_apps_overview():
    if len(applications.keys()) == 0:
        return []
    overview, i = [[]], 0
    for key in applications.keys():
        overview[i].append((applications[key].name, key, applications[key].description))
        if len(overview[i]) == 2:
            i += 1
            overview.append([]) 

    return overview

def get_models_by_app(app_name: str):
    models = []
    restriction = []
    first = True
    for key in applications[app_name].models.keys():
        model = applications[app_name].models[key]
        models.append((model.name, model.name.replace(" ", "-"), model.description, ", ".join(model.file_format), first))
        first = False

        if len(restriction) == 0:
            restriction = set(model.file_format)
        else:
            restriction = restriction.intersection(set(model.file_format))
    
    return models, ", ".join(list(restriction))

def config():
    global CONFIG, applications
    try:
        CONFIG = parse_json.parse_config(CONFIG_PATH)
        applications = parse_json.parse_applications(CONFIG["models_path"])
        parse_json.parse_models(applications)
        CONFIG["number_of_random_pictures"], CONFIG["random_picture_list"] = pictures.number_of_pictures_in_folder(CONFIG["random_pictures_path"])
        return True
    except FileNotFoundError as err:
        print(err)
        return False
    except Exception as e:
        print("An unknown error ocurred", e)
        return False

if __name__ == "__main__":
    if config():
        app.run(port=CONFIG["port"], debug=True)