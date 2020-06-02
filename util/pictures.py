from os import listdir, rename
from os.path import isfile, join
import random

def number_of_pictures_in_folder(folder_path: str):
    i = 0
    pictureList = []
    for f in listdir(folder_path):
        if isfile(join(folder_path, f)):     
            i += 1
            pictureList.append(f)
            
    return i, pictureList

def random_pictures(n: int, pictureList: list):
    
    """
    This function returns "n" different numbers

    n (Int): quantity of numbers to return
    min (Int): minimum random number
    max (Int): maximum random number
    """
    used = set()
    output = [[]]
    i = 0
    while len(used) < n:
        r = random.randrange(0, len(pictureList)-1)
        if r not in used:
            used.add(r)
            output[i].append(pictureList[r])
    return output



