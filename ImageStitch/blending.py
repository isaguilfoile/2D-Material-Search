# For background and shading correction for microscopy images
# Microscope image preprocessing before stitching & Flake recognition
# https://github.com/peng-lab/BaSiCPy/

import jax
jax.config.update('jax_platform_name', 'cpu')

from basicpy import BaSiC
from basicpy import datasets as bdata
from matplotlib import pyplot as plt

import os
import cv2 as cv
import imageio.v2 as imageio
import numpy as np

def main():
    # Create an output directory if it doesn't exist
    output_dir = "ImageStitch/output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Delete all files in output_dir before saving new images
    for file in os.listdir(output_dir):
        file_path = os.path.join(output_dir, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

    raw_img_dir = "ImageStitch/microscope_images"
    if not os.path.exists(raw_img_dir):
        print("Error: Images do not exist")

    image_files = sorted([os.path.join(raw_img_dir, f) for f in os.listdir(raw_img_dir) if f.endswith(".jpg")])

    images = np.array([imageio.imread(img) for img in image_files])
    # print(images[1].shape)

    # images = bdata.timelapse_brightfield()
    # print(images.shape)

    print(images.shape)
    if images.shape[-1] < 10:
        images = images[:, :, :, 0] # Remove depth channel
    print(images.shape)

    images = images.astype(np.float32) / 255.0

    # Display a sample image
    # plt.imshow(images[2])
    # plt.title("Sample Image")
    # plt.show()

    # Fit the flatfield and darkfield
    basic = BaSiC(get_darkfield=True, smoothness_flatfield=1)
    basic.fit(images)

    # Plot the fit results
    fig, axes = plt.subplots(1, 3, figsize=(9, 3))
    im = axes[0].imshow(basic.flatfield)
    fig.colorbar(im, ax=axes[0])
    axes[0].set_title("Flatfield")
    im = axes[1].imshow(basic.darkfield)
    fig.colorbar(im, ax=axes[1])
    axes[1].set_title("Darkfield")
    axes[2].plot(basic.baseline)
    axes[2].set_xlabel("Frame")
    axes[2].set_ylabel("Baseline")
    fig.tight_layout()

    # Correct the original images
    images_transformed = basic.transform(
    images,
    )

    # Save the corrected images
    for i, img_corrected in enumerate(images_transformed):
        output_path = os.path.join(output_dir, f"{i:03d}.jpg")
        imageio.imwrite(output_path, (img_corrected * 255).astype(np.uint8))

    # Plot the corrected results

if __name__ == "__main__":
    main()