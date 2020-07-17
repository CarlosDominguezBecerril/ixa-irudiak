class Model:
    def __init__(self, short_name, name, description, model_info, file_format):
        self.short_name = short_name
        self.name = name
        self.description = description
        self.model_info = model_info
        self.file_format = file_format
    
    def __str__(self):
        attributes = ""
        return "\tShort name: {} Model name: {}. Model description: {}. Model info: {}. Accepted file format: {}".format(self.shortName, self.name, self.description, self.model_info, attributes, self.file_format)