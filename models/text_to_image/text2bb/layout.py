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
from torchvision.utils import make_grid

from PIL import Image

# draw graphs
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def boxes_to_layout(vecs, boxes, obj_to_img, H, W=None, pooling='sum'):
    """
    Inputs:
    - vecs: Tensor of shape (O, D) giving vectors
    - boxes: Tensor of shape (O, 4) giving bounding boxes in the format
      [x0, y0, x1, y1] in the [0, 1] coordinate space
    - obj_to_img: LongTensor of shape (O,) mapping each element of vecs to
      an image, where each element is in the range [0, N). If obj_to_img[i] = j
      then vecs[i] belongs to image j.
    - H, W: Size of the output

    Returns:
    - out: Tensor of shape (N, D, H, W)
    """
    O, D = vecs.size()
    if W is None:
        W = H

    grid = _boxes_to_grid(boxes, H, W)

    # If we don't add extra spatial dimensions here then out-of-bounds
    # elements won't be automatically set to 0
    img_in = vecs.view(O, D, 1, 1).expand(O, D, 8, 8)
    sampled = F.grid_sample(img_in, grid, align_corners=True)   # (O, D, H, W)

    # Explicitly masking makes everything quite a bit slower.
    # If we rely on implicit masking the interpolated boxes end up
    # blurred around the edges, but it should be fine.
    # mask = ((X < 0) + (X > 1) + (Y < 0) + (Y > 1)).clamp(max=1)
    # sampled[mask[:, None]] = 0

    out = _pool_samples(sampled, obj_to_img, pooling=pooling)

    return out

def _boxes_to_grid(boxes, H, W):
    """
    Input:
    - boxes: FloatTensor of shape (O, 4) giving boxes in the [x0, y0, x1, y1]
      format in the [0, 1] coordinate space
    - H, W: Scalars giving size of output

    Returns:
    - grid: FloatTensor of shape (O, H, W, 2) suitable for passing to grid_sample
    """
    O = boxes.size(0)

    boxes = boxes.view(O, 4, 1, 1)

    # All these are (O, 1, 1)
    x0, y0 = boxes[:, 0], boxes[:, 1]
    x1, y1 = boxes[:, 2], boxes[:, 3]
    ww = x1 - x0
    hh = y1 - y0

    X = torch.linspace(0, 1, steps=W).view(1, 1, W).to(boxes)
    Y = torch.linspace(0, 1, steps=H).view(1, H, 1).to(boxes)

    X = (X - x0) / ww   # (O, 1, W)
    Y = (Y - y0) / hh   # (O, H, 1)

    # Stack does not broadcast its arguments so we need to expand explicitly
    X = X.expand(O, H, W)
    Y = Y.expand(O, H, W)
    grid = torch.stack([X, Y], dim=3)  # (O, H, W, 2)

    # Right now grid is in [0, 1] space; transform to [-1, 1]
    grid = grid.mul(2).sub(1)

    return grid


def _pool_samples(samples, obj_to_img, pooling='sum'):
    """
    Input:
    - samples: FloatTensor of shape (O, D, H, W)
    - obj_to_img: LongTensor of shape (O,) with each element in the range
      [0, N) mapping elements of samples to output images

    Output:
    - pooled: FloatTensor of shape (N, D, H, W)
    """
    dtype, device = samples.dtype, samples.device
    O, D, H, W = samples.size()
    N = obj_to_img.data.max().item() + 1

    # Use scatter_add to sum the sampled outputs for each image
    out = torch.zeros(N, D, H, W, dtype=dtype, device=device)
    idx = obj_to_img.view(O, 1, 1, 1).expand(O, D, H, W)
    out = out.scatter_add(0, idx, samples)

    if pooling == 'avg':
        # Divide each output mask by the number of objects; use scatter_add again
        # to count the number of objects per image.
        ones = torch.ones(O, dtype=dtype, device=device)
        obj_counts = torch.zeros(N, dtype=dtype, device=device)
        obj_counts = obj_counts.scatter_add(0, obj_to_img, ones)
        print(obj_counts)
        obj_counts = obj_counts.clamp(min=1)
        out = out / obj_counts.view(N, 1, 1, 1)
    elif pooling != 'sum':
        raise ValueError('Invalid pooling "%s"' % pooling)

    return out

def draw_bounding_boxes_layout(img, obj, boxes, path, size=(64, 64)):
    fig, ax = plt.subplots(1, figsize=(15,15))
    ax.imshow(img.permute(1, 2, 0))
    labels, k = [], 0
    color = ["#FF0000","#00FF00", "#0000FF", "#FFFF00", "#00FFFF", "#FF00FF", "#0099FF", "#EB70AA", "#F0D58C", "#F4A460", "#FFD700", "#6495ED", "#000000", "#FFFFFF"]
    for i in boxes.numpy()[:-1]:
        width = (i[2] - i[0])*size[0]
        height = (i[3] - i[1])*size[1]
        x, y = i[0] * size[0], i[1]*size[1]
        rect = patches.Rectangle((x, y),width, height,linewidth=3, edgecolor=color[k],facecolor='none')
        labels.append(obj[k])
        ax.add_patch(rect)
        k+=1
    plt.legend(labels)
    plt.savefig(path)