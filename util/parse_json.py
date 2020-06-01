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
                applications[app["short_name"]] = Application(app["name"], app["description"], app["path"])

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