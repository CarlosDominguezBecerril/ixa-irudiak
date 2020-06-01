# ixa-irudiak

## Libraries used

> pip install flask 
> pip install flask-bootstrap

## How to create an application

1 Open models/modelsConfig.json file
2 Create your own application with the following content.

**short_name**: Short name that is going to be used with in the application
**name**: Name of the application that is going to be displayed
**description**: Description of the application that is going to be displayed.
**path**: Application models location

Example:
> {   
    "short_name": "myApp",
    "name": "my application",
    "description": "My application description",
    "path": "./models/myapplication"
}

## How to include a model in your application

1 Create a folder in the path specified by your application
2 Create a new json file with the following content

**name**: Name of the model.
**description**: Description of the model.
**model_path**: Path where the model is located.
**attributes**: Attributes of the model than can be modified.
**file_format**: Supported file formats

Example:
>{
    "name": "model1",
    "description": "model1 description",
    "model_path" : "./models/image_captioning/model1.h5",
    "attributes" : [],
    "file_format": [".jpg", ".jpeg", ".png"]
}

Additional information:
**Attributes supported by "attributes"**: None.
**formats accepted by "file_format"**: The ones supported by HTML5