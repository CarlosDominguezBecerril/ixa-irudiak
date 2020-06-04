from domain.application import Application
from domain.model import Model

import random

from models.image_captioning.caption_generation_oier import run_model as oier

def run_all_models(models_list: list, app_name: str, applications: dict, user_input:str):
    """
    This function runs all the models in models_list.

    models_list (list): List with the models name (string).
    app_name (str): The name of app used by the user.
    application (dict): Application list.
    user_input (str): The input given by the user. Text or path to a file.
    """
    output = []
    for model in models_list:
        if app_name not in applications or model not in applications[app_name].models:
            continue
        else:
            # For each model create a list with model name, the output of executing the model and the application type
            output.append([model, execute_model(app_name, applications[app_name].models[model], user_input, applications[app_name].app_type), applications[app_name].app_type])
    return output

def execute_model(app_name: str, model: Model, user_input: str, app_type: str):
    """
    This function runs the application function where the model is located.

    app_name (str): The name of app used by the user.
    user_input (str): The input given by the user. Text or path to a file.
    model (Model): model that is going to be used to retrieve the information.
    app_type (str): application output type. text or image path.
    """

    # Image captioning application
    if app_name == "image_cap":
        return run_image_cap(model, user_input)

    # Application not found. type: picture
    if app_type == "image":
        return "../static/pictures/image_error.jpg"

    # Application not found. type: text
    return "'{}' application can't be found in the system".format(app_name)

def run_image_cap(model: Model, user_input: str):
    """
    This function join together all the models related with image captioning.

    user_input (str): The input given by the user. Text or path to a file.
    model (Model): model that is going to be used to retrieve the information.
    """

    output = ""
    # Using try catch for not having dependencies with errors in tensorflow, pytorch ....
    try:
        # Model 'Oier'
        if model.name == "Oier":
            output = oier.run_model(user_input, model.model_info)
        else:
        # model not found
            output = "'{}' model can't be found in the system".format(model.name)
        
    except:
        output = "Serious error found when trying to use '{}' model".format(model.name)

    return output