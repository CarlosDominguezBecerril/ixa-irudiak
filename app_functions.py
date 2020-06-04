from flask import Flask, render_template, url_for, send_from_directory, request
from domain.application import Application
from domain.model import Model
from util import parse_json, pictures
import os
from os import listdir
from os.path import isfile, join
from werkzeug.utils import secure_filename

import random

from execute_models import run_all_models

def random_picture_input(appNames:list, app_name:str, data:dict, applications:dict, CONFIG:dict):
    """
    Function that handles random pictures

    appNames (List): Menu generated.
    app_name (str): The name of app used by the user
    data (dict): values that the user uses in the form
    applications (dict): Application list
    CONFIG (dict): configuration of the server
    """

    # Check if the application exist
    if app_name in applications:
        picture_name = ""
        # find the key in the dictionary that contains the file of the picture
        if "model" in data:
            if data['model'] in applications[app_name].models:
                picture_name = "randomPicture" + data['model']
            else:
                # Model doesn't exist
                return render_template("wrongOutput.html", menu = appNames, title = applications[app_name].name, info= "The model doesn't exist")
        else:
            picture_name = "randomPicture"

        if picture_name in data:
            models_list = []
            # Retrieve selected model list
            if 'model' in data:
                models_list.append(data['model'])
            else:
                for i in data:
                    if i.startswith("checkbox"):
                        mod = i[8:]
                        if mod in applications[app_name].models:
                            models_list.append(mod)
            # No models selected
            if len(models_list) == 0:
                return render_template("wrongOutput.html", menu = appNames, title = applications[app_name].name, info= "You didn't select a model!. Try again")
            # Retrieve allowed files
            allowed_files = retrieve_allowed_files(models_list, app_name, applications)

            picture_in_system = False
            for f in listdir(CONFIG["random_pictures_path"] + "/"):
                if isfile(join(CONFIG["random_pictures_path"] + "/", f)) and f == data[picture_name]:
                    picture_in_system = True

            if picture_in_system:
                # check if correct file extension
                if "." + data[picture_name].split('.')[1] not in allowed_files:
                    return render_template("wrongOutput.html", menu = appNames, title = applications[app_name].name, info= "File extension not valid. Try again")
                
                # Execute the models
                output = run_all_models(models_list, app_name, applications, CONFIG["random_pictures_path"] + "/" + data[picture_name])
               
                return render_template("output.html", menu = appNames, title = applications[app_name].name, allowed_file = allowed_files, models = output, app = applications[app_name].name, picture = CONFIG["random_pictures_path"] + "/" + data[picture_name])
            else:
                return render_template("wrongOutput.html", menu = appNames, title = applications[app_name].name, info= "The picture doesn't exist in our system")
        else:
            return render_template("wrongOutput.html", menu = appNames, title = applications[app_name].name, info= "Error while trying to retrieve the random picture")
    return render_template("wrongOutput.html", menu = appNames, title = "Error", info= "Application name not found")

def user_file_input(appNames:list, app_name:str, data:dict, applications:dict, CONFIG:dict):

    """
    Function that handles the pictures uploaded by a user

    appNames (List): Menu generated.
    app_name (str): The name of app used by the user
    data (dict): values that the user uses in the form
    applications (dict): Application list
    CONFIG (dict): configuration of the server
    """
    # Case when user uploads a picture
    if 'userFile' not in request.files:
        return render_template("wrongOutput.html", menu = appNames, title = applications[app_name].name, test = app_name, info= "The file couldn't be upload to the server. Try again")
    
    # Search for the uploaded file
    file = request.files['userFile']

    # Error if nothing is sent
    if file.filename == '':
        return render_template("wrongOutput.html", menu = appNames, title = applications[app_name].name, test = app_name, info= "You didn't select a file. Try again")

    # Search for the name of the application
    if app_name in applications:

        models_list = []
        # Retrieve selected model list
        if 'model' in data:
            if data['model'] in applications[app_name].models:
                models_list.append(data['model'])
            else:
                # Model doesn't exist
                return render_template("wrongOutput.html", menu = appNames, title = applications[app_name].name, info= "The model doesn't exist")
        else:
            for i in data:
                if i.startswith("checkbox"):
                    mod = i[8:]
                    if mod in applications[app_name].models:
                        models_list.append(mod)
        # No models selected
        if len(models_list) == 0:
            return render_template("wrongOutput.html", menu = appNames, title = applications[app_name].name, info= "You didn't select a model!. Try again")

        # Retrieve allowed files
        allowed_files = retrieve_allowed_files(models_list, app_name, applications)
        # Save the file
        if file and "." + file.filename.split(".")[1] in allowed_files:
            filename = secure_filename(file.filename)
            file.save(os.path.join(CONFIG["upload_folder"], filename))
            
            # Execute the models
            output = run_all_models(models_list, app_name, applications, CONFIG["upload_folder"] + "/" + file.filename)

            return render_template("output.html", menu = appNames, title = applications[app_name].name, allowed_file = allowed_files, models = output, app = applications[app_name].name, picture = CONFIG["upload_folder"] + "/" + file.filename)
        else:
            return render_template("wrongOutput.html", menu = appNames, title = applications[app_name].name, info= "File extension not valid. Try again")

    return render_template("wrongOutput.html", menu = appNames, title = "Error", info= "Application name not found")

def retrieve_allowed_files(models_name_list:list, app_name:str, applications: dict):

    """
    Function that handles the allowed files of given models name. In case of more than one models the intersection of all of them is made.

    app_name (str): The name of app used by the user
    models_name_list (list): names of the models
    applications (dict): Application list
    """

    allowed_files = set()
    for i in models_name_list:
        if len(allowed_files) == 0:
            allowed_files = set(applications[app_name].models[i].file_format)
        else:
            allowed_files = allowed_files.intersection(set(applications[app_name].models[i].file_format))
    return allowed_files

def fake_values(models_name_list: list):

    """
    This function generates some fake values for each model in the list.

    models_name_list (list): List of the models names
    """
    output = []
    for i in models_name_list:
        output.append([i, random.randint(0, 10000)])
    return output


def get_menu_items(selected_item:str, applications: dict):

    """
    This function returns a list with the values of the menu. For each of the we add the short name, the name and a boolean to specify
    if the item needs to be highlighted

    selected_item (str): Element to be highlighted
    applications (dict): list of applications

    """
    # Home value
    menu_items = [["", "Home", False]]

    # Highlight if it is the selected item
    if selected_item == "Home":
        menu_items[0][2] = True

    # For each application
    for i in applications.keys():
        menu_items.append([i, applications[i].name, False])
        # Highlight if it is the selected item
        if i == selected_item:
            menu_items[-1][2] = True
    return menu_items

def get_apps_overview(applications: dict):

    """
    This function retrieves an overview of the applications (application name and description)

    applications (dict): list of applications
    """
    # If no applications return an empty list
    if len(applications.keys()) == 0:
        return []
    
    # Add the information of each application.
    overview, i = [[]], 0
    for key in applications.keys():
        overview[i].append((applications[key].name, key, applications[key].description))

        # Every two applications we create a new list inside (this if for aesthetics of the webpage).
        if len(overview[i]) == 2:
            i += 1
            overview.append([]) 

    return overview

def get_models_by_app(app_name: str, applications: dict):

    """
    This function retrieves information (model name, model description and allowed file formats) and restriction of each model.

    app_name (str): name of the application
    applications (dict): list of applications

    """
    models = []
    restriction = []

    # Iterate through all the models
    for key in applications[app_name].models.keys():
        # get the model and append the information
        model = applications[app_name].models[key]
        models.append([model.name, model.description, ", ".join(model.file_format), False])

        # Restrictions taking into account all the models (used for comparing models)
        if len(restriction) == 0:
            restriction = set(model.file_format)
        else:
            restriction = restriction.intersection(set(model.file_format))

    # The first model needs to be to True in order to activate the first "tab" of the HTML code
    if len(models) > 0:
        models[0][3] = True

    return models, ", ".join(list(restriction))
