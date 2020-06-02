from flask import Flask, render_template, url_for, send_from_directory, request
from flask_bootstrap import Bootstrap
from domain.application import Application
from domain.model import Model
from util import parse_json, pictures
import os
from werkzeug.utils import secure_filename

import random

app = Flask(__name__)
Bootstrap(app)

CONFIG_PATH = "config.json"
CONFIG = None
applications = None

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
    appNames = get_menu_items(app_name)
    data = request.form
    if 'userFile' not in request.files:
        return render_template("wrongOutput.html", menu = appNames, title = applications[app_name].name, test = app_name, info= "The file couldn't be upload to the server. Try again")
    file = request.files['userFile']
    if file.filename == '':
        return render_template("wrongOutput.html", menu = appNames, title = applications[app_name].name, test = app_name, info= "You didn't select a file. Try again")
    if app_name in applications:
        allowed_files = set()
        models_list = []
        if "model" in data:
            models_list.append([data["model"], random.randint(1, 10000)])
            allowed_files = set(applications[app_name].models[data["model"]].file_format)
        else:
            for i in data:
                models_list.append([i[8:], random.randint(1, 10000)])
                if len(allowed_files) == 0:
                    allowed_files = set(applications[app_name].models[models_list[-1][0]].file_format)
                else:
                    allowed_files = allowed_files.intersection(set(applications[app_name].models[models_list[-1][0]].file_format))

        if file and "." + file.filename.split(".")[1] in allowed_files:
            filename = secure_filename(file.filename)
            file.save(os.path.join(CONFIG["upload_folder"], filename))
            return render_template("output.html", menu = appNames, title = applications[app_name].name, allowed_file = allowed_files, models = models_list, app = applications[app_name].name, picture = CONFIG["upload_folder"] + "/" + file.filename)
    return render_template("wrongOutput.html", menu = appNames, title = applications[app_name].name, info= "File extension not valid. Try again")

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