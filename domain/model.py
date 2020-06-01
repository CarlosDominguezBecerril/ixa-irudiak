class Model:
    def __init__(self, name, description, model_path, attributes, file_format):
        self.name = name
        self.description = description
        self.model_path = model_path
        self.attributes = []
        self.file_format = file_format
    
    def __str__(self):
        attributes = ""
        return "\tModel name: {}. Model description: {}. Model path: {}, Model attributes: {}. Accepted file format: {}".format(self.name, self.description, self.model_path, attributes, self.file_format)