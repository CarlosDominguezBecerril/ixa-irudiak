# ixa-irudiak

## Pictures

Homepage

![alt text](githubPictures/homepage.png "Homepage")

Application overview

![alt text](githubPictures/imageCaptioning.png "Application overview")

Compare models of an application

![alt text](githubPictures/modelCompare.png "Compare models of an application")

Results

![alt text](githubPictures/results.png "Results")

## Libraries used

Some libraries may not be necessary if you are using your own models.

> pip install flask==1.1.2

> pip install nltk==3.5

> pip install scipy==1.4.1

> pip install Keras==2.3.1

> pip install tensorflow==2.2.0

> pip install Pillow==7.2.0

> pip install matplotlib==3.3.2

> pip install scikit-learn==0.23.1

> pip install numpy==1.19.0

> pip install torch==1.5.1

> pip install torchvision==0.6.1

> pip install torchtext==0.6.0

> pip install tabulate==0.8.7

> pip install spacy==2.3.2

> pip install imageio==2.9.0

In order to ease the installation you can just:

> pip install -r requirements.txt

Spacy english parser:
> python -m spacy download en

## Running the web server

1 Download the pretrained models folder from [here](https://drive.google.com/file/d/1bnLbhr9QT2iLkqNJDhKlQOOSOGn6P9VI/view?usp=sharing) an extract it in the root directory.

2 Execute app.py (you may need root permissions. This can be done running "sudo -s" in the terminal.)

3 Open your web browser and search for "localhost:port", by default "localhost:80" or simply "localhost". The port can be changed in config.json.

## How to create an application

1 Open models/modelsConfig.json file

2 Create your own application with the following content.

**short_name**: Short name that is going to be used with in the application.

**name**: Name of the application that is going to be displayed.

**description**: Description of the application that is going to be displayed.

**path**: Application models location.

**type**: Application type. Valid values: "image" and "text".

**show**: Optional. Either to show the application or not. Valid values: true | false.

Example:
```
{   
    "short_name": "myApp",
    "name": "my application",
    "description": "My application description",
    "path": "./models/myapplication",
    "type": "text",
    "show": true
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

    output = []
    # Using try catch for not having dependencies with errors in tensorflow, pytorch ....
    try:
        # Model 'model1'
        # The short_name is the name but without blanks
        if model.short_name == "model1":
            with Pool(1) as p:
                model_output = p.apply(model1.run_model, (user_input, model.model_info))
            output.append(["Output", model_output, "text"])
        # Model 'model2'
        elif model.short_name == "model2":
            with Pool(1) as p:
                model_output = p.apply(model2.run_model, (user_input, model.model_info))
            output.append(["Output", model_output[0], "text"])
            output.append(["Attention plot", model_output[1], "image"])
        # add as many as you have

        else:
            # model not found
            output.append(["Error in system",  "'{}' model can't be found in the system".format(model.name), "text"])
        
    except Exception as e:
        output.append(["Error in model",  "Serious error found when trying to use '{}' model. Error: {}".format(model.name, e), "text"])

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
        return [["Application not found", "../static/pictures/image_error.jpg", "image"]]

    # Application not found. type: text
    return [["Application not found", "'{}' application can't be found in the system".format(app_name), "text"]]

```

## How to include a model in your application

**Note:** an application is needed before adding a model

1 Create a folder in the path specified in your application.

2 Create a new json file with the following content.

**name**: Name of the model.

**description**: Description of the model.

**model_info**: Here you add the information you may need in order to use your model.

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
    "file_format": [".jpg", ".jpeg", ".png"]
}
```

3 Open "execute_models.py" python file

4 In the function that handle the models of the application add a new "if / elif" statement that calls to the function that predicts the output. imports of libraries may be needed.

Important: each element that you add to output is written like this: [name, model_output, type]

**name**: Name that is going to be displayed in the output
**model_output**: The output that you get from the execution of the model.
**type**: "image" or "text". In the case of "image" model_output needs to be the path to the picture and in the case of "text" model_output is a text.

Code to add:
```
# Model 'model2'
# short_name is the name given to the model but without blanks
elif model.short_name == "model2":
    # We call to our function model2.run_model() that predicts the output
        with Pool(1) as p:
            model_output = p.apply(model2.run_model, (user_input, model.model_info))
        output.append(["Output", model_output[0], "text"])
        output.append(["Attention plot", model_output[1], "image"])
```
Example:

```
def run_my_application2(model: Model, user_input: str):
    """
    This function join together all the models related with application2.

    user_input (str): The input given by the user. Text or path to a file.
    model (Model): model that is going to be used to retrieve the information.
    """

    output = []
    # Using try catch for not having dependencies with errors in tensorflow, pytorch ....
    try:

        # HERE WE ADD THE IF / ELIF STATEMENT

        # Model 'model1'
        # The short_name is the name but without blanks
        if model.short_name == "model1":
            with Pool(1) as p:
                model_output = p.apply(model1.run_model, (user_input, model.model_info))
            output.append(["Output", model_output, "text"])
        # Model 'model2'
        elif model.short_name == "model2":
            with Pool(1) as p:
                model_output = p.apply(model2.run_model, (user_input, model.model_info))
            output.append(["Output", model_output[0], "text"])
            output.append(["Attention plot", model_output[1], "image"])
        # add as many as you have

        else:
            # model not found
            output.append(["Error in system",  "'{}' model can't be found in the system".format(model.name), "text"])
        
    except Exception as e:
        output.append(["Error in model",  "Serious error found when trying to use '{}' model. Error: {}".format(model.name, e), "text"])

    return output
```



Additional information:

**Formats accepted by "file_format"**: The ones supported by HTML5

## Configuration file

File used to configure the application. The default name is "config.json" and it is located in "root". To change the file location edit the variable "CONFIG_PATH" located in "app.py".

*Compulsory arguments:*

**models_path**: path where the models are located.

**random_pictures_path**: path where the random picture are located (always starting with "/static")

**random_texts_path**: path where the random texts are located (always starting with "/static")

**upload_folder**: path where the pictures sent by the users are going to be uploaded (always starting with "/static")

*Non compulsory arguments:*

**port**: Port that the server is going to use

**number_of_pictures_to_show**: Number of random pictures that are showed in each application

**number_of_texts_to_show**: Number of random texts that are showed in each application

Example
```
{
    "port": 80,
    "models_path": "models/modelsConfig.json",
    "random_pictures_path": "static/randomPictures",
    "random_texts_path": "static/randomTexts",
    "number_of_pictures_to_show": 8,
    "number_of_texts_to_show": 5,
    "upload_folder": "static/tmp"
}
```
