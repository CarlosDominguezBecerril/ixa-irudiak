from domain.application import Application
from domain.model import Model

import random

from models.image_captioning.ShowAndTell import run_model as oier
from models.image_captioning.ShowAttendAndTell import run_model as gorka
from models.text_to_image.text2bb import run_model as text2bb

from multiprocessing import Pool
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
            # For each model create a list with model name and the output of executing the model
            output.append([applications[app_name].models[model].name, execute_model(app_name, applications[app_name].models[model], user_input, applications[app_name].app_type)])
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
    # Text to image application
    elif app_name == "text_to_image":
        return run_text_to_image(model, user_input)
    # Application not found. type: picture
    if app_type == "image":
        return [["Application not found", "../static/pictures/image_error.jpg", "image"]]

    # Application not found. type: text
    return [["Application not found", "'{}' application can't be found in the system".format(app_name), "text"]]

def run_text_to_image(model: Model, user_input: str):
    """
    This function join together all the models related with image captioning.

    user_input (str): The input given by the user. Text or path to a file.
    model (Model): model that is going to be used to retrieve the information.
    """

    output = []
    # Using try catch for not having dependencies with errors in tensorflow, pytorch ....
    try:
        # Model 'sg2im'
        if model.short_name == "TextToBoundingBoxV1":
            with Pool(1) as p:
                model_output = p.apply(text2bb.run_model, (user_input, model.model_info))
            output.append(["Output", model_output[0], "image"])
            output.append(["Scene graph", model_output[1], "image"])
            output.append(["Objects list", model_output[2], "text"])
            output.append(["Relations list", model_output[3], "text"])
            output.append(["Triples list", model_output[4], "text"])
        elif model.short_name == "TextToBoundingBoxV2":
            with Pool(1) as p:
                model_output = p.apply(text2bb.run_model, (user_input, model.model_info))
            output.append(["Output", model_output[0], "image"])
            output.append(["Scene graph", model_output[1], "image"])
            output.append(["Objects list", model_output[2], "text"])
            output.append(["Relations list", model_output[3], "text"])
            output.append(["Triples list", model_output[4], "text"])
        elif model.short_name == "TextToBoundingBoxV3":
            with Pool(1) as p:
                model_output = p.apply(text2bb.run_model, (user_input, model.model_info))
            output.append(["Output", model_output[0], "image"])
            output.append(["Scene graph", model_output[1], "image"])
            output.append(["Objects list", model_output[2], "text"])
            output.append(["Relations list", model_output[3], "text"])
            output.append(["Triples list", model_output[4], "text"])
        else:
        # model not found
            output.append(["Error in system",  "'{}' model can't be found in the system".format(model.name), "text"])
        
    except Exception as e:
        output.append(["Error in model",  "Serious error found when trying to use '{}' model. Error: {}".format(model.name, e), "text"])
    return output

def run_image_cap(model: Model, user_input: str):
    """
    This function join together all the models related with image captioning.

    user_input (str): The input given by the user. Text or path to a file.
    model (Model): model that is going to be used to retrieve the information.
    """

    output = []
    # Using try catch for not having dependencies with errors in tensorflow, pytorch ....
    try:
        # Model 'Oier'
        if model.short_name == "ShowAndTell":
            with Pool(1) as p:
                model_output = p.apply(oier.run_model, (user_input, model.model_info))
                # smodel_output = oier.run_model(user_input, model.model_info)
            output.append(["Output", model_output, "text"])
        elif model.short_name == "ShowAttendAndTell":
            with Pool(1) as p:
                model_output = p.apply(gorka.run_model, (user_input, model.model_info))
            output.append(["Output", model_output[0], "text"])
            output.append(["Attention plot", model_output[1], "image"])
        else:
        # model not found
            output.append(["Error in system",  "'{}' model can't be found in the system".format(model.name), "text"])
        
    except Exception as e:
        output.append(["Error in model",  "Serious error found when trying to use '{}' model. Error: {}".format(model.name, e), "text"])
    return output