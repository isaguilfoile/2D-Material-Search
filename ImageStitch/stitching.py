# For stitching together our grid of images from the microscope
# We should try this file with/without preprocessing from background & shading correction
# We will use multiview_stitcher

# We will need the translation offset (positions) or each tile
# I think images can be given in any numpy compatible array

# TODO: When gathering images, can we save the servo positions at each capture somehow then load it in this file?
# We only have 2D layout, but this can be used if the Z-axis is ever added to the system

# Image files are stored in /images/
# Image file names and corresponding locations are stored in /files/image_dt.csv

# 1) Prepare the data for stitching

import pandas as pd
import numpy as np

import os
import sys

from skimage.io import imread

from multiview_stitcher import spatial_image_utils as si_utils
from multiview_stitcher import vis_utils, msi_utils, fusion, registration

import matplotlib.pylab as plt

dt_path = "files/test.csv" # TODO: Change to "files/image_dt.csv"
image_directory = "MotorMover/CameraTest" # TODO: Change to "images/raw"

# Load image metadata
df = pd.read_csv(dt_path)

# Load images and create tiles with position metadata
tiles_with_position_info = []

for _, row in df.iterrows():
    image_path = os.path.join(image_directory, row['Image Name'])
    img = imread(image_path)

    tile = si_utils.get_sim_from_array(
        img,
        dims=['y', 'x', 'c'],
        translation={
            'x': row['X Position'],
            'y': row['Y Position']
        },
        transform_key='grid_arrangement'
    )
    tiles_with_position_info.append(tile)

# Fuse using stage position transforms
stitched = fusion.fuse(
    tiles_with_position_info,
    transform_key='grid_arrangement',
    blending_widths={'y': 50, 'x': 50}, # TODO: Adjust as needed
).compute()

# Select first time point and arrange axes
stitched = stitched.sel(t=0).transpose('y', 'x', 'c').data

# Visualize stitched result
plt.figure(figsize=(10, 10))
plt.imshow(stitched)
plt.axis('off')
plt.title("stitched image")
plt.show()