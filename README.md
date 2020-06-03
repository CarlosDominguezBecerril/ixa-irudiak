# ixa-irudiak

## Libraries used

> pip install flask 

## Running the web server

Execute app.py

## How to create an application

1 Open models/modelsConfig.json file

2 Create your own application with the following content.

**short_name**: Short name that is going to be used with in the application.

**name**: Name of the application that is going to be displayed.

**description**: Description of the application that is going to be displayed.

**path**: Application models location.

Example:
> {   

>    "short_name": "myApp",

>   "name": "my application",

>   "description": "My application description",

>    "path": "./models/myapplication"

>}

## How to include a model in your application

1 Create a folder in the path specified in your application.

2 Create a new json file with the following content.

**name**: Name of the model.

**description**: Description of the model.

**model_path**: Path where the model is located.

**attributes**: Attributes of the model than can be modified.

**file_format**: Supported file formats

Example:
>{

>    "name": "model1",

>    "description": "model1 description",

>    "model_path" : "./models/image_captioning/model1.h5",

>    "attributes" : [],

>    "file_format": [".jpg", ".jpeg", ".png"]

>}

Additional information:

**Attributes supported by "attributes"**: None.

**Formats accepted by "file_format"**: The ones supported by HTML5

## Configuration file

File used to configure the application. The default name is "config.json" and it is located in "root". To change the the file location edit the variable "CONFIG_PATH" located in "app.py".

*Compulsory arguments:*

**models_path**: path where the models are located.

**random_pictures_path**: path where the random picture are located (always starting with "/static")

**upload_folder**: path where the pictures sent by the users are going to be uploaded (always starting with "/static")

*Non compulsory arguments:*

**port**: Port that the server is going to use

**number_of_pictures_to_show**: Number of random pictures that are showed in each application


Example
>{

>"port": 80,

>"models_path": "models/modelsConfig.json",

>"random_pictures_path": "static/randomPictures",

>"number_of_pictures_to_show": 8,

>"upload_folder": "static/tmp"

>}