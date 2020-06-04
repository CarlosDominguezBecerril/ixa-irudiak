# ixa-irudiak

## Libraries used

> pip install flask

> pip install nltk

> pip install Keras

> pip install tensorflow

> pip install Pillow

## Running the web server

Execute app.py

## How to create an application

1 Open models/modelsConfig.json file

2 Create your own application with the following content.

**short_name**: Short name that is going to be used with in the application.

**name**: Name of the application that is going to be displayed.

**description**: Description of the application that is going to be displayed.

**path**: Application models location.

**type**: Application type. Valid values: "image" and "text".

Example:
```
{   
    "short_name": "myApp",
    "name": "my application",
    "description": "My application description",
    "path": "./models/myapplication",
    "type: "text"
}
```

3 Open "execute_models.py" python file

4 Create a function in order to handle the models of the application.

Example

```
def run_my_application2(model: Model, user_input: str):
    """
    This function join together all the models related with application2.

    user_input (str): The input given by the user. Text or path to a file.
    model (Model): model that is going to be used to retrieve the information.
    """

    output = ""
    # Using try catch for not having dependencies with errors in tensorflow, pytorch ....
    try:
        # Model 'model1'
        if model.name == "model1":
            output = model1.run_model(user_input, model.model_info)
        # Model 'model2'
        elif model.name == "model2":
            output = model2.run_model(user_input, model.model_info)
        # add as many as you have
        else:

        # model not found (text error)
            output = "'{}' model can't be found in the system".format(model.name)
        # model not found (image error)
        #   output = "../static/pictures/image_error.jpg"

    except:

        # model error (text error)
        output = "Serious error found when trying to use '{}' model".format(model.name)
        # model error (image error)
        #   output = "../static/pictures/image_error.jpg"

    return output
```

5 In function execute_model include the function that you have created in step 4 adding a new "if / elif statement"

Code to add
```
# application 2
elif app_name == "myapplication2":
    return run_my_application2(model, user_input)

```
Example

```
def execute_model(app_name: str, model: Model, user_input: str, app_type: str):
    """
    This function runs the application function where the model is located.

    app_name (str): The name of app used by the user.
    user_input (str): The input given by the user. Text or path to a file.
    model (Model): model that is going to be used to retrieve the information.
    app_type (str): application output type. text or image path.
    """

    # HERE WE INCLUDE THE INFORMATION

    # application 1
    if app_name == "myapplication1":
        return run_my_application1(model, user_input)

    # application 2
    elif app_name == "myapplication2":
        return run_my_application2(model, user_input)

    # Application not found. type: picture
    if app_type == "image":
        return "../static/pictures/image_error.jpg"

```

## How to include a model in your application

**Note:** an application is needed before adding a model

1 Create a folder in the path specified in your application.

2 Create a new json file with the following content.

**name**: Name of the model.

**description**: Description of the model.

**model_info**: Here you add the information you may need in order to use your model.

**attributes**: Attributes of the model than can be modified.

**file_format**: Supported file formats

Example:
```
{
    "name": "model1",
    "description": "model1 description",
    "model_info" : {
        "tokenizer" : "./models/myapplication/tokenizer.pkl",
        "max_length": 34,
        "best_model" : "./models/myapplication/model.h5"
    },
    "attributes" : [],
    "file_format": [".jpg", ".jpeg", ".png"]
}
```

3 Open "execute_models.py" python file

4 In the function that handle the models of the application add a new "if / elif" statement that calls to the function that predicts the output. imports of libraries may be needed.

Code to add:
```
# Model 'model2'
elif model.name == "model2":
    # We call to our function model2.run_model() that predicts the output
    output = model2.run_model(user_input, model.model_info)
```
Example:

```
def run_my_application2(model: Model, user_input: str):
    """
    This function join together all the models related with image captioning.

    user_input (str): The input given by the user. Text or path to a file.
    model (Model): model that is going to be used to retrieve the information.
    """

    output = ""
    # Using try catch for not having dependencies with errors in tensorflow, pytorch ....
    try:
        # HERE WE ADD THE NEW IF / ELIF STATEMEN

        # Model 'model1'
        if model.name == "model1":
            output = model1.run_model(user_input, model.model_info)
        # Model 'model2'
        elif model.name == "model2":
            output = model2.run_model(user_input, model.model_info)
        # add as many as you have
        else:

        # model not found (text error)
            output = "'{}' model can't be found in the system".format(model.name)
        # model not found (image error)
        #   output = "../static/pictures/image_error.jpg"

    except:

        # model error (text error)
        output = "Serious error found when trying to use '{}' model".format(model.name)
        # model error (image error)
        #   output = "../static/pictures/image_error.jpg"

    return output
```



Additional information:

**Attributes supported by "attributes"**: None.

**Formats accepted by "file_format"**: The ones supported by HTML5

## Configuration file

File used to configure the application. The default name is "config.json" and it is located in "root". To change the file location edit the variable "CONFIG_PATH" located in "app.py".

*Compulsory arguments:*

**models_path**: path where the models are located.

**random_pictures_path**: path where the random picture are located (always starting with "/static")

**upload_folder**: path where the pictures sent by the users are going to be uploaded (always starting with "/static")

*Non compulsory arguments:*

**port**: Port that the server is going to use

**number_of_pictures_to_show**: Number of random pictures that are showed in each application


Example
```
{
    "port": 80,
    "models_path": "models/modelsConfig.json",
    "random_pictures_path": "static/randomPictures",
    "number_of_pictures_to_show": 8,
    "upload_folder": "static/tmp"
}
```
