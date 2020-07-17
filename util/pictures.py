from os import listdir, rename
from os.path import isfile, join
import random

def retrieve_pictures_names_in_folder(folder_path: str):
    """
    This functions returns a list with the file names of a given folder.
    
    folder_path (str): path of the folder that we are going to check
    """
    pictureList = []
    # Iterate through all the elements in the folder "folder_path"
    for f in listdir(folder_path):
        # if its a file then add it to the list
        if isfile(join(folder_path, f)):     
            pictureList.append(f)
            
    return pictureList

def random_pictures(n: int, pictureList: list):
    
    """
    This function returns "n" different numbers

    n (Int): quantity of numbers to return
    pictureList (list): picture names list
    """
    if n >= len(pictureList):
        return pictureList
    elif n <= 0:
        return []

    used = set()
    while len(used) < n:
        r = random.randrange(0, len(pictureList))
        # If the picture is not in the list add it
        if pictureList[r] not in used:
            used.add(pictureList[r])
    return list(used)



