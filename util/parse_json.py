from domain.application import Application
from domain.model import Model
import json
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

    args = ["short_name", "name", "path", "description"]

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

        # Create a new "Application" with the values given
        if validJson:
            if app["short_name"] in applications:
                print("There is already an application with the name: {}".format(app["short_name"]))
            else:
                applications[app["short_name"].replace(" ", "")] = Application(app["name"], app["description"], app["path"])

    return applications

def parse_models(applicationList: dict):

    """
    Given a dictionary of "Applications" instanciate the models related for each "application"

    applicationList (Dictionary): dictionary with the "Applications"
    """
    for app in applicationList.keys():
        parse_application_model(applicationList[app])
        

def parse_application_model(application: Application):

    """
    Given an "Application" instanciate the models found in "Application.models_path"

    application (Application): application
    """
    files = [f for f in listdir(application.models_path) if isfile(join(application.models_path, f))]
    args = ["name", "description", "model_path", "attributes", "file_format"]
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
            application.add_model(Model(data["name"], data["description"], data["model_path"], data["attributes"], data["file_format"]))

def parse_config(config_path: str):

    """
    Given the path of the configuration file returns a dictionary with all the elements.

    config_path(String): Path to a json file. 

    """
    with open(config_path) as f:
        data = json.load(f)

    compulsory_args = ["models_path", "random_pictures_path", "upload_folder"]
    non_compulsory_args = ["port", "number_of_pictures_to_show"]
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
        if arg == "random_pictures_path":
            if data[arg][-1] == "/":
                data[arg]  = data[arg][:-1]
    # Non compulsory arguments
    for arg in non_compulsory_args:
        if arg not in data:
            if arg == "port":
                data["port"] = 5000
            elif arg == "number_of_pictures_to_show":
                data["number_of_pictures_to_show"] = 4

    # Error arguments
    for arg in error_arguments:
        if arg in data:
            raise FileNotFoundError("The argument '{}' in '{}' cannot be used".format(arg, config_path))
    return data