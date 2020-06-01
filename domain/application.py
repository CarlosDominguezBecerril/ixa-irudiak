from domain.model import Model

class Application:
    def __init__(self, name: str, description: str, models_path:str):
        self.name = name
        self.description = description
        self.models_path = models_path
        self.models = {}
    
    def add_model(self, content: Model):
        if content.name in self.models:
            print("The model is already in the list")
        else:
            self.models[content.name] = content

    def remove_model(self, model_name: str):
        result = self.models.pop(model_name, False)

        if not result:
            print("The model {} doesn't exist".format(model_name))

    
    def __str__(self):
        models = []
        for i in self.models.keys():
            models.append(str(self.models[i]) + "\n")
        return "Application name: {}.\nApplication description: {}.\nApplication models path: {}.\nNumber of models: {}.\nModels: \n{}".format(self.name, self.description, self.models_path, len(self.models), "".join(models))

