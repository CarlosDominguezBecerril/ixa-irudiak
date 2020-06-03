from flask import Flask, render_template, url_for, send_from_directory, request
from domain.application import Application
from domain.model import Model
from util import parse_json, pictures
import os
from os import listdir
from os.path import isfile, join
from werkzeug.utils import secure_filename

import random

def random_picture_input(appNames, app_name, data, applications, CONFIG):
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
            allowed_files = retrieve_allowed_files(models_list, app_name, applications, CONFIG)

            picture_in_system = False
            for f in listdir(CONFIG["random_pictures_path"] + "/"):
                if isfile(join(CONFIG["random_pictures_path"] + "/", f)) and f == data[picture_name]:
                    picture_in_system = True

            if picture_in_system:
                # check if correct file extension
                if "." + data[picture_name].split('.')[1] not in allowed_files:
                    return render_template("wrongOutput.html", menu = appNames, title = applications[app_name].name, info= "File extension not valid. Try again")
                # Execute the models
                output = fake_values(models_list)
                return render_template("output.html", menu = appNames, title = applications[app_name].name, allowed_file = allowed_files, models = output, app = applications[app_name].name, picture = CONFIG["random_pictures_path"] + "/" + data[picture_name])
            else:
                return render_template("wrongOutput.html", menu = appNames, title = applications[app_name].name, info= "The picture doesn't exist in our system")
        else:
            return render_template("wrongOutput.html", menu = appNames, title = applications[app_name].name, info= "Error while trying to retrieve the random picture")
    return render_template("wrongOutput.html", menu = appNames, title = "Error", info= "Application name not found")

def user_file_input(appNames, app_name, data, applications, CONFIG):

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
        allowed_files = retrieve_allowed_files(models_list, app_name, applications, CONFIG)
        # Save the file
        if file and "." + file.filename.split(".")[1] in allowed_files:
            filename = secure_filename(file.filename)
            file.save(os.path.join(CONFIG["upload_folder"], filename))
            # Execute the models
            output = fake_values(models_list)
            return render_template("output.html", menu = appNames, title = applications[app_name].name, allowed_file = allowed_files, models = output, app = applications[app_name].name, picture = CONFIG["upload_folder"] + "/" + file.filename)
        else:
            return render_template("wrongOutput.html", menu = appNames, title = applications[app_name].name, info= "File extension not valid. Try again")

    return render_template("wrongOutput.html", menu = appNames, title = "Error", info= "Application name not found")

def retrieve_allowed_files(models_name_list, app_name, applications, CONFIG):

    """
    Function that handles the allowed files of given models
    app_name (str): The name of app used by the user
    models_name_list (list): names of the models
    applications (dict): Application list
    CONFIG (dict): configuration of the server
    """

    allowed_files = set()
    for i in models_name_list:
        if len(allowed_files) == 0:
            allowed_files = set(applications[app_name].models[i].file_format)
        else:
            allowed_files = allowed_files.intersection(set(applications[app_name].models[i].file_format))
    return allowed_files

def fake_values(models_name_list):

    """
        This function creates some fake values for each model in the list.
        models_name_list (list): List of the models names
    """
    output = []
    for i in models_name_list:
        output.append([i, random.randint(0, 10000)])
    return output
