'''
RESOURCES:
https://py.imagej.net/en/latest/Initialization.html
'''

import imagej
import os

ij = imagej.init('sc.fiji:fiji') # Create ImageJ2 gateway including Fiji plugins
print(f"ImageJ version: {ij.getVersion()}")

image_folder = "/sub_images"
output_folder = "/output"

# Create a list of all the images in the folder
sub_images = sorted([f for f in os.listdir(image_folder) if f.endswith(('.tif', '.jpg', '.png'))])
if not sub_images:
    raise ValueError(f"No images found in specified directory: {image_folder}")

# Convert list to Fiji-compatible format
sub_images_str = '\n'.join([os.path.join(image_folder, img) for img in sub_images])

# Run the Grid/Collection stitching plugin
args = {
        'type': 'Filename defined position',  # Choose 'Grid: row-by-row' if applicable
    'order': 'Left & Down',  # Adjust based on acquisition order
    'grid_size_x': 2,  # Adjust grid size based on your dataset
    'grid_size_y': 2,   # Adjust as needed
    'overlap': 10,  # Percentage overlap (adjust based on your images)
    'fusion_method': 'Linear Blending',  # Options: Linear Blending, Max Intensity, Min Intensity
    'regression_threshold': 0.30,  
    'max/avg_displacement_threshold': 2.50,
    'absolute_displacement_threshold': 3.50,
    'compute_overlap': True,  # Enable overlap computation
    'display_fused_image': True,  # Show the final stitched image
    'save_fused_image': True,
    'fused_image_output_directory': output_folder  # Save output
}

ij.py.run_plugin("Grid/Collection stitching", args)

# Close ImageJ when done
ij.dispose()