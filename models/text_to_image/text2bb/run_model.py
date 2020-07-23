import os

import numpy as np

import json

import torch
import torchvision
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as T
from torch.utils.data import random_split
import torchtext
from torchvision.utils import make_grid, save_image

from PIL import Image
import random

import models.text_to_image.text2bb.sng_parser as sg
from models.text_to_image.text2bb.layout import draw_bounding_boxes_layout, boxes_to_layout
from models.text_to_image.text2bb.model import Sg2ImModel
from models.text_to_image.text2bb.vis import draw_scene_graph

import pickle

def get_default_device():
    """Pick GPU if available, else CPU"""
    if torch.cuda.is_available():
        return torch.device('cuda')
    else:
        return torch.device('cpu')

def to_device(data, device):
    """Move tensor(s) to chosen device"""
    if isinstance(data, (list,tuple)):
        return [to_device(x, device) for x in data]
    return data.to(device, non_blocking=True)

def generate_graph_info(text):
    # Scene graph parser
    graph = sg.parse(text)
        
    # If there is at least one relation add it to the dataset
    if len(graph['relations']) > 0:
        # Parse the graph
        objects, relations, triples = [], set(), []
        obj_map = {}
        for relation in graph['relations']:
            sub, rel, obj = relation['subject'], relation['relation'], relation['object']
            relations.add(rel)
            if sub not in obj_map:
                obj_map[sub] = len(obj_map)
                objects.append(graph['entities'][sub]['head'])
            if obj not in obj_map:
                obj_map[obj] = len(obj_map)
                objects.append(graph['entities'][obj]['head'])
            triples.append([[graph['entities'][sub]['head'], obj_map[sub]], rel, [graph['entities'][obj]['head'], obj_map[obj]]])
    else:
        raise "The graph generate by the text has no relations"
    
    return objects, list(relations), triples 
    
def predict_single(text, model, device, path, vocab, size):
    objs, rels, triples = generate_graph_info(text)
    objs_list = list(objs)
    rels_list = list(rels)
    triples_list0 = [[s[0], p, o[0]] for s, p, o in triples]
    triples_list1 = [[s[1], p, o[1]] for s, p, o in triples]

    objs, triples, obj_to_img = model.encode_scene_graph(objs, rels, triples)

    # Generate a random name for the output
    random_name = generate_random_names() 
    file_path = path + "/" + random_name + '.png'
    file_path_graph = path + "/" + random_name + 'graph.png'

    # Generate the scene graph
    draw_scene_graph(objs_list, triples_list1, file_path_graph, orientation='V')

    # Process the layout
    objs, triples, obj_to_img = to_device(objs, device), to_device(triples, device), to_device(obj_to_img, device)
    preds = model(objs, triples, obj_to_img)
    
    # Generate layout picture
    v = [[0, 0, 0]]*len(preds)
    vecs = to_device(torch.FloatTensor(v), device)
    out = boxes_to_layout(vecs, preds, obj_to_img, size[1], size[0], pooling='sum')
    save_image(out.data, file_path)
    
    # Show layout picture
    IMAGENET_MEAN = [0.485, 0.456, 0.406]
    IMAGENET_STD = [0.229, 0.224, 0.225]

    transforms = T.Compose([T.ToTensor(), T.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)])
    draw_bounding_boxes_layout(transforms(Image.open(file_path).convert("RGB")), objs_list, preds.cpu().detach(), file_path, size=size)
    return file_path, file_path_graph, objs_list, rels_list, triples_list0

def generate_random_names(length = 20, base = 64):
    """
    This function generates a random name of a given length

    length (int): length of the output
    base (int): base to be used in order to generate the random name

    """
    characters = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+-"
    # Upper and lower bounds control
    if base > 64:
        base = 64
    elif base < 2:
        base = 0
    output_name = []

    # Generate de name
    for _ in range(length):
        output_name.append(characters[random.randint(0, base-1)])

    return "".join(output_name)

def run_model(text: str, model_values: dict):
    with open(model_values['vocab'], "r") as json_file:
        vocab = json.load(json_file)
    device = get_default_device()
    model = to_device(Sg2ImModel(vocab, embedding_dim=64), device)
    model.load_state_dict(torch.load(model_values['checkpoint_dir'], map_location=torch.device('cpu') ))
    output = predict_single(text, model, device, model_values['layout_dir'], vocab, size = (model_values['width'], model_values['height']))
    return ["../" + output[0], "../" + output[1], output[2], output[3], output[4]]
