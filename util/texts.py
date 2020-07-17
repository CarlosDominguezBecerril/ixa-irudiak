from os import listdir, rename
from os.path import isfile, join
import random

def retrieve_texts_names_in_folder(folder_path: str):
    """
    This functions returns a list with the file names of a given folder.
    
    folder_path (str): path of the folder that we are going to check
    """
    textList = []
    # Iterate through all the elements in the folder "folder_path"
    for f in listdir(folder_path):
        # if its a file then add it to the list
        if isfile(join(folder_path, f)):     
            textList.append(f)
            
    return textList

def read_text_file(path: str):
    """
    This function returns a list with the file name and the contents of the file split by lines

    path (str): path where the file is located 
    """
    with open(path, 'r') as file:
        output = file.readlines()

    return output
    
def random_texts(n: int, textsList: list, path:str):
    
    """
    This function returns "n" different numbers

    n (Int): quantity of numbers to return
    textsList (list): texts filenames list

    output (tuple): tuple of filename and the content of the file
    """
    output = []
    if n >= len(textsList):
        for i in range(len(textsList)):
            tmp = read_text_file(path + "/" +  textsList[i])
            if len(tmp) == 0:
                output.append([textsList[i], ""])
            else:
                output.append([textsList[i], tmp[0]])
        return output
    elif n <= 0:
        return []

    used = set()
    while len(used) < n:
        r = random.randrange(0, len(textsList))
        # If the picture is not in the list add it
        if textsList[r] not in used:
            used.add(textsList[r])
            tmp = read_text_file(path + "/" +  textsList[r])
            if len(tmp) == 0:
                output.append([textsList[r], ""])
            else:
                output.append([textsList[r], tmp[0]])
    return output



