from domain.application import Application
from domain.model import Model
import json
import os
from os import listdir
from os.path import isfile, join

def parse_applications(app_path: str):

    """
    Function that parse app_path file.

    app_path (String): Path to a json file. 

    """
    applications = {}

    with open(app_path) as f:
        data = json.load(f)

    args = ["short_name", "name", "path", "description", "type"]
    allowed_types = set(["image", "text"])
    # If applications attribute doesn't exist finish immediately
    if "applications" not in data:
        return {}

    for app in data["applications"]:  
        validJson = True

        # Check if "app" has all the requirements
        for arg in args:
            if arg not in app:
                print("Missing argument {} in file {}".format(arg, app_path))
                validJson = False
            if arg == "type" and app[arg] not in allowed_types:
                print("The type {} is not allowed. Error found in file {}".format(app[arg], app_path))
                validJson = False

        # Create a new "Application" with the values given
        if validJson:
            if app["short_name"] in applications:
                print("There is already an application with the name: {}".format(app["short_name"]))
            elif 'show' in app and app['show'] == False:
                print("The show value is set to false. Not showing this application")
            else:
                applications[app["short_name"].replace(" ", "")] = Application(app["name"], app["description"], app["path"], app['type'])

    return applications

def parse_models(applicationList: dict):

    """
    Given a dictionary of "Applications" instanciate the models related for each "application"

    applicationList (Dictionary): dictionary with the "Applications"
    """
    for app in list(applicationList.keys()):
        parse_application_model(applicationList[app])
        if len(applicationList[app].models) == 0:
            print("{} doesn't have any model associated. Removing this application...".format(applicationList[app].name))
            applicationList.pop(app, None)
        

def parse_application_model(application: Application):

    """
    Given an "Application" instanciate the models found in "Application.models_path"

    application (Application): application
    """
    files = [f for f in listdir(application.models_path) if isfile(join(application.models_path, f))]
    args = ["name", "description", "model_info", "file_format"]
    for model_path in files:
        with open(application.models_path + "/"+ model_path) as f:
            data = json.load(f)
        validJson = True    
        # Check if the model fulfill all the requirements
        for arg in args:
            if arg not in data:
                print("Missing argument {} in file {}. The model is not going to be included".format(arg, application.models_path + "/"+ model_path))
                validJson = False

        # Add the model to the application
        if validJson:
            application.add_model(Model(data["name"].replace(" ", ""), data["name"], data["description"], data["model_info"], data["file_format"]))

def parse_config(config_path: str):

    """
    Given the path of the configuration file returns a dictionary with all the elements.

    config_path(String): Path to a json file. 

    """
    with open(config_path) as f:
        data = json.load(f)

    compulsory_args = ["models_path", "random_pictures_path", "random_texts_path", "upload_folder"]
    non_compulsory_args = ["port", "number_of_pictures_to_show", "number_of_texts_to_show"]
    error_arguments = ["number_of_random_pictures"]

    # Compulsory arguments
    for arg in compulsory_args:
        if arg not in data:
            raise FileNotFoundError("Missing argument '{}' in '{}'".format(arg, config_path))
        if arg == "upload_folder":
            if not (data[arg].startswith("/static") or data[arg].startswith("static")):
                raise FileNotFoundError("Argument '{}' needs to be inside 'static' folder. Actual path: {}".format(arg, data[arg]))
            else:
                if data[arg][-1] == "/":
                    data[arg]  = data[arg][:-1]
                # Create folder if needed
                if not os.path.exists(data[arg]):
                    print("Creating folder: {}".format(data[arg]))
                    os.makedirs(data[arg])
                else:
                    # Remove files in the folder
                    for f in listdir(data[arg]):
                        if isfile(join(data[arg], f)):
                            os.remove(join(data[arg], f))

        if arg == "random_pictures_path":
            if not (data[arg].startswith("/static") or data[arg].startswith("static")):
                raise FileNotFoundError("Argument '{}' needs to be inside 'static' folder. Actual path: {}".format(arg, data[arg]))
            else:
                if data[arg][-1] == "/":
                    data[arg]  = data[arg][:-1]
        elif arg == "random_texts_path":
            if not (data[arg].startswith("/static") or data[arg].startswith("static")):
                raise FileNotFoundError("Argument '{}' needs to be inside 'static' folder. Actual path: {}".format(arg, data[arg]))
            else:
                if data[arg][-1] == "/":
                    data[arg]  = data[arg][:-1]

    # Non compulsory arguments
    for arg in non_compulsory_args:
        if arg not in data:
            if arg == "port":
                data["port"] = 5000
            elif arg == "number_of_pictures_to_show":
                data["number_of_pictures_to_show"] = 4
            elif arg == "number_of_texts_to_show": 
                data['number_of_texts_to_show'] = 5

    # Error arguments
    for arg in error_arguments:
        if arg in data:
            raise FileNotFoundError("The argument '{}' in '{}' cannot be used".format(arg, config_path))
    return data