from flask import Flask, render_template, url_for, send_from_directory, request
from domain.application import Application
from domain.model import Model
from util import parse_json, pictures, texts
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
               
                return render_template("outputImage.html", menu = appNames, title = applications[app_name].name, allowed_file = allowed_files, models = output, app = applications[app_name].name, picture = CONFIG["random_pictures_path"] + "/" + data[picture_name])
            else:
                return render_template("wrongOutput.html", menu = appNames, title = applications[app_name].name, info= "The picture doesn't exist in our system")
        else:
            return render_template("wrongOutput.html", menu = appNames, title = applications[app_name].name, info= "Error while trying to retrieve the random picture")
    return render_template("wrongOutput.html", menu = appNames, title = "Error", info= "Application name not found")


def random_text_input(appNames:list, app_name:str, data:dict, applications:dict, CONFIG:dict):
    """
    Function that handles random texts

    appNames (List): Menu generated.
    app_name (str): The name of app used by the user
    data (dict): values that the user uses in the form
    applications (dict): Application list
    CONFIG (dict): configuration of the server
    """

    # Check if the application exist
    if app_name in applications:
        text_name = ""
        # find the key in the dictionary that contains the file of the text
        if "model" in data:
            if data['model'] in applications[app_name].models:
                text_name = "randomText" + data['model']
            else:
                # Model doesn't exist
                return render_template("wrongOutput.html", menu = appNames, title = applications[app_name].name, info= "The model doesn't exist")
        else:
            text_name = "randomText"

        if text_name in data:
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

            text_in_system = False
            for f in listdir(CONFIG["random_texts_path"] + "/"):
                if isfile(join(CONFIG["random_texts_path"] + "/", f)) and f == data[text_name]:
                    text_in_system = True

            if text_in_system:
                # check if correct file extension
                if "." + data[text_name].split('.')[1] not in allowed_files:
                    return render_template("wrongOutput.html", menu = appNames, title = applications[app_name].name, info= "File extension not valid. Try again")
                
                output_text = texts.read_text_file(CONFIG["random_texts_path"] + "/" + data[text_name])
                if len(output_text) == 0:
                    output_text = ""
                else:
                    output_text = output_text[0]
                # Execute the models
                output = run_all_models(models_list, app_name, applications, output_text)
                return render_template("outputText.html", menu = appNames, title = applications[app_name].name, allowed_file = allowed_files, models = output, app = applications[app_name].name, text = output_text)
            else:
                return render_template("wrongOutput.html", menu = appNames, title = applications[app_name].name, info= "The text doesn't exist in our system")
        else:
            return render_template("wrongOutput.html", menu = appNames, title = applications[app_name].name, info= "Error while trying to retrieve the random text")
    return render_template("wrongOutput.html", menu = appNames, title = "Error", info= "Application name not found")

def custom_input(appNames:list, app_name:str, data:dict, applications:dict, CONFIG:dict):
    """
    Function that handles custom text

    appNames (List): Menu generated.
    app_name (str): The name of app used by the user
    data (dict): values that the user uses in the form
    applications (dict): Application list
    CONFIG (dict): configuration of the server
    """
    # Check if the application exist
    if app_name in applications:
        input_location_key = ""
        # find the key in the dictionary that contains the file of the text
        if "model" in data:
            if data['model'] in applications[app_name].models:
                input_location_key = "custom-input" + data['model']
            else:
                # Model doesn't exist
                return render_template("wrongOutput.html", menu = appNames, title = applications[app_name].name, info= "The model doesn't exist")
        else:
            input_location_key = "custom-input"

        if input_location_key in data:
            input_content = data[input_location_key]

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

            if applications[app_name].app_type == "text":
                # Execute the models
                output = run_all_models(models_list, app_name, applications, input_content)
                return render_template("outputText.html", menu = appNames, title = applications[app_name].name, allowed_file = ["Custom text input"], models = output, app = applications[app_name].name, text = input_content)
            else:
                return render_template("wrongOutput.html", menu = appNames, title = applications[app_name].name, info= "Application type not valid")
        else:
            return render_template("wrongOutput.html", menu = appNames, title = applications[app_name].name, info= "Error while trying to retrieve your text")
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
        extension = "." + file.filename.split(".")[1]
        # Save the file
        if file and extension in allowed_files:
            filename = secure_filename(file.filename)
            file.save(os.path.join(CONFIG["upload_folder"], filename))
            new_name = generate_random_names() + extension
            os.rename(os.path.join(CONFIG["upload_folder"], filename), os.path.join(CONFIG["upload_folder"], new_name))

            if applications[app_name].app_type == "image":
                # Execute the models
                output = run_all_models(models_list, app_name, applications, CONFIG["upload_folder"] + "/" + new_name)
                return render_template("outputImage.html", menu = appNames, title = applications[app_name].name, allowed_file = allowed_files, models = output, app = applications[app_name].name, picture = CONFIG["upload_folder"] + "/" + new_name)
            elif applications[app_name].app_type == "text":
                # Execute the models
                output_text = texts.read_text_file(CONFIG["upload_folder"] + "/" + new_name)
                if len(output_text) == 0:
                    output_text = ""
                else:
                    output_text = output_text[0]
                output = run_all_models(models_list, app_name, applications, output_text)
                return render_template("outputText.html", menu = appNames, title = applications[app_name].name, allowed_file = allowed_files, models = output, app = applications[app_name].name, text = output_text)
            else:
                return render_template("wrongOutput.html", menu = appNames, title = applications[app_name].name, info= "Application type not valid")
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
        models.append([model.short_name, model.description, ", ".join(model.file_format), False, model.name])

        # Restrictions taking into account all the models (used for comparing models)
        if len(restriction) == 0:
            restriction = set(model.file_format)
        else:
            restriction = restriction.intersection(set(model.file_format))

    # The first model needs to be to True in order to activate the first "tab" of the HTML code
    if len(models) > 0:
        models[0][3] = True

    return models, ", ".join(list(restriction))

def generate_random_names(length = 20, base = 64):
    """
    This function generates a random name of a given length

    length (int): length of the output
    base (int): base to be used in order to generate the random name

    """
    characters = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+-"
    # Upper and lower bounds control
    if base > 64:
        base = 64
    elif base < 2:
        base = 0
    output_name = []

    # Generate de name
    for _ in range(length):
        output_name.append(characters[random.randint(0, base-1)])

    return "".join(output_name)