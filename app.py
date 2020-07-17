from flask import Flask, render_template, url_for, send_from_directory, request
from domain.application import Application
from domain.model import Model
from util import parse_json, pictures, texts
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
from werkzeug.utils import secure_filename
import app_functions

import random

app = Flask(__name__)
CONFIG_PATH = "config.json"
CONFIG = {}
applications = {}

@app.route('/')
def index():
    """
    This function generates an overview of all the applications.
    """
    return render_template("index.html", title = "index", menu = app_functions.get_menu_items("Home", applications), applications = app_functions.get_apps_overview(applications))

@app.route('/<app_name>')
def application(app_name:str):
    """
    This function genererates the "app_name" page.

    app_name (str): name of the application that the user is requesting
    """
    # Menu generation
    appNames = app_functions.get_menu_items(app_name, applications)

    # Check if the application exists otherwise 404 error.
    if app_name in applications:
        # Retrieve the models information and restrictions (file restrictions)
        modelsList, restriction = app_functions.get_models_by_app(app_name, applications)

        # Depending on the application type return the appropiate template
        if applications[app_name].app_type == 'image':
            return render_template("applicationImage.html", compare = restriction, title = applications[app_name].name, app = app_name, menu = appNames, models = modelsList, pictures = pictures.random_pictures(CONFIG["number_of_pictures_to_show"], CONFIG["random_picture_list"]))
        elif applications[app_name].app_type == 'text':
            return render_template("applicationText.html", compare = restriction, title = applications[app_name].name, app = app_name, menu = appNames, models = modelsList, texts = texts.random_texts(CONFIG["number_of_texts_to_show"], CONFIG["random_text_list"], CONFIG["random_texts_path"]))
    
    return render_template("404.html", menu = appNames), 404 

@app.route('/<app_name>/output', methods=['POST'])
def output(app_name:str):
    """
    This function handles the input that the user gives (file uploaded by a user or random picture) and gives an output.

    app_name (str): name of the application that the user is requesting
    """
    # Menu generation
    appNames = app_functions.get_menu_items(app_name, applications)

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
    elif "random-text" == method:
        return app_functions.random_text_input(appNames, app_name, data, applications, CONFIG)
    elif "custom-text" == method:
        return app_functions.custom_input(appNames, app_name, data, applications, CONFIG)

    # Any other "method" gives an error
    return render_template("wrongOutput.html", menu = appNames, title = applications[app_name].name, info= "Unexpected error")

@app.errorhandler(404)
def page_not_found(e):

    """
    This function handles 404 errors.
    """
    return render_template("404.html", title = "404", menu = app_functions.get_menu_items("", applications)), 404

def config():

    """
    This function configurates the global variables "applications" and "CONFIG".
    """
    global CONFIG, applications
    try:
        # Parse configuration file
        CONFIG = parse_json.parse_config(CONFIG_PATH)

        # Parse applications
        applications = parse_json.parse_applications(CONFIG["models_path"])
        
        # Parse models
        parse_json.parse_models(applications)

        # Information about random pictures
        CONFIG["random_picture_list"] = pictures.retrieve_pictures_names_in_folder(CONFIG["random_pictures_path"])
        CONFIG["number_of_random_pictures"] = len(CONFIG["random_picture_list"])
        CONFIG["random_text_list"] = texts.retrieve_texts_names_in_folder(CONFIG['random_texts_path'])
        CONFIG["number_of_random_texts"] = len(CONFIG["random_text_list"])
        return True
    except FileNotFoundError as err:
        print(err)
        return False
    except Exception as e:
        print("An unknown error ocurred", e)
        return False

if __name__ == "__main__":

    # If the configuration is valid start the server
    if config():
        app.run(host= '0.0.0.0', port=CONFIG["port"])