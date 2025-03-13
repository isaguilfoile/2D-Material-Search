"""
https://github.com/yfukai/m2stitch
https://m2stitch.readthedocs.io/en/latest/
"""

from os import path
import os

import numpy as np
import pandas as pd
from PIL import Image

import m2stitch

def main():
    # Create output directory if it doesn't exist
    output_dir = "ImageStitch/output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    image_dir = "ImageStitch/microscope_images"

    output_npy = "ImageStitch/subimages.npy"
    output_csv = "ImageStitch/subimages_props.csv"

    # Get a sorted list of image files (assuming they are named in a grid order)
    image_files = sorted([f for f in os.listdir(image_dir) if f.endswith(".jpg")])

    # print(image_files)

    # Load images as grayscale (or adjust as needed)
    images = [np.array(Image.open(os.path.join(image_dir, img)).convert("L")) for img in image_files]

    # Convert to NumPy array with shape (num_images, heigth, width)
    images_array = np.stack(images, axis=0)

    # Save the images as a NumPy array
    np.save(output_npy, images_array)

    # Define row and column positions manually or based on filesnames
    # Assuming images are named in a "row_col.jpg" format (e.g., "1_2.jpg")
    rows, cols = [], []
    for img in image_files:
        row, col = map(int, img.split(".")[0].split("_")) # Extract row & col from filename
        rows.append(row)
        cols.append(col)

    # Create DataFrame
    props_df = pd.DataFrame({"row": rows, "col": cols})

    # Save to CSV
    props_df.to_csv(output_csv, index=True)

    script_path = path.dirname(path.realpath(__file__))

    image_file_path = path.join(script_path, "subimages.npy")
    props_file_path = path.join(script_path, "subimages_props.csv")
    images = np.load(image_file_path)
    props = pd.read_csv(props_file_path, index_col=0)

    print(props)

    rows = props["row"].to_list()
    cols = props["col"].to_list()

    print(images.shape) # Must be 3-dim, with each dimension meaning (tile_index, x, y)
    print(rows) # The row indicies for each tile index
    print(cols) # The column indices for each tile index

    # Perform image stitching
    result_df,_ = m2stitch.stitch_images(images, rows, cols, pou = 50, row_col_transpose=False, ncc_threshold=1)

    print(result_df["y_pos"]) # The absolute y position of tiles
    print(result_df["x_pos"]) # The absolute x position of the tiles

    # stitching example
    result_df["y_pos2"] = result_df["y_pos"] - result_df["y_pos"].min()
    result_df["x_pos2"] = result_df["x_pos"] - result_df["x_pos"].min()

    size_y = images.shape[1]
    size_x = images.shape[2]

    stitched_image_size = (
        result_df["y_pos2"].max() + size_y,
        result_df["x_pos2"].max() + size_x,
    )
    stitched_image = np.zeros_like(images, shape=stitched_image_size)
    for i, row in result_df.iterrows():
        stitched_image[
            row["y_pos2"] : row["y_pos2"] + size_y,
            row["x_pos2"] : row["x_pos2"] + size_x,
        ] = images[i]

    result_image_file_path = path.join(script_path, "stitched_image.npy")
    np.save(result_image_file_path, stitched_image)


if __name__ == "__main__":
    main()

