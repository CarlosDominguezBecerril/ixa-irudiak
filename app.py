from flask import Flask, render_template, url_for
from flask_bootstrap import Bootstrap
from domain.application import Application
from domain.model import Model
from util import parse_json

app = Flask(__name__)
Bootstrap(app)

MODELS_PATH = "models/modelsConfig.json"
applications = None

@app.route('/')
def index():
    return render_template("index.html", menu = get_menu_items(), applications = get_apps_overview())

@app.route('/<app_name>')
def application(app_name):
    appNames = get_menu_items()

    if app_name in applications:
        return render_template("aplication.html", menu = appNames, models = get_models_by_app(app_name))
    else:
       return render_template("404.html", menu = appNames), 404 

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", menu = get_menu_items()), 404

def get_menu_items():
    menu_items = []
    for i in applications.keys():
        menu_items.append((i, applications[i].name))
    return menu_items

def get_apps_overview():

    if len(applications.keys()) == 0:
        return []
    
    overview, i = [[]], 0
    for key in applications.keys():
        overview[i].append((applications[key].name, key, applications[key].description))
        if len(overview[i]) == 2:
            i += 1
            overview.append([]) 

    return overview

def get_models_by_app(app_name: str):
    models = []
    first = True
    for key in applications[app_name].models.keys():
        model = applications[app_name].models[key]
        models.append((model.name, model.name.replace(" ", "-"), model.description, model.file_format, first))
        first = False

    return models
if __name__ == "__main__":
    try:
        applications = parse_json.parse_applications(MODELS_PATH)
        parse_json.parse_models(applications)
        # Debug
        #for i in applications.keys():
        #    print(applications[i])
        #print(get_apps_overview())
        #print(get_menu_items())
        app.run(debug=True)
    except FileNotFoundError as err:
        print(err)