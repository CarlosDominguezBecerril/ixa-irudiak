from domain.model import Model

class Application:
    def __init__(self, name: str, description: str, models_path:str, app_type:str):
        self.name = name
        self.description = description
        self.models_path = models_path
        self.models = {}
        self.app_type = app_type
    
    def add_model(self, content: Model):
        """
        This function adds a model to the application

        content (Model): model to include
        """
        if content.name in self.models:
            print("The model is already in the list")
        else:
            self.models[content.name] = content

    def remove_model(self, model_name: str):
        """
        This function removes a model from the application

        model_name (str): name of the model to delete
        """
        result = self.models.pop(model_name, False)
        if not result:
            print("The model {} doesn't exist".format(model_name))

    
    def __str__(self):
        models = [] 
        for i in self.models.keys():
            models.append(str(self.models[i]) + "\n")
        return "Application name: {}.\nApplication description: {}.\nApplication models path: {}.\nNumber of models: {}.\nModels: \n{}Type: {}\n".format(self.name, self.description, self.models_path, len(self.models), "".join(models), self.app_type)

