from os import listdir, rename
from os.path import isfile, join
import random

def number_of_pictures_in_folder(folder_path: str):
    """
    This functions returns a list with the file names of a given folder.
    
    folder_path (str): path of the folder that we are going to check
    """
    i = 0
    pictureList = []
    # Iterate through all the elements in the folder "folder_path"
    for f in listdir(folder_path):
        # if its a file then add it to the list
        if isfile(join(folder_path, f)):     
            i += 1
            pictureList.append(f)
            
    return i, pictureList

def random_pictures(n: int, pictureList: list):
    
    """
    This function returns "n" different numbers

    n (Int): quantity of numbers to return
    pictureList (list): picture names list
    """
    used = set()
    output = [[]]
    i = 0
    while len(used) < n:
        r = random.randrange(0, len(pictureList)-1)
        # If the picture is not in the list add it
        if r not in used:
            used.add(r)
            output[i].append(pictureList[r])
    return output



