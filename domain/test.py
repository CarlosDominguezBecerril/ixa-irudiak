from domain.application import Application

a = Application("name", "description", "path")

def print_Application(a):
    print(a.name)
    print(a.description)
    print(a.models_path)
    print(a.models)

print_Application(a)

a.remove_model("dsf")

print_Application(a)

a.add_model("aaa", {"bbbb": 2, "aaaa": 3})

print_Application(a)

a.remove_model("aaa")

print_Application(a)