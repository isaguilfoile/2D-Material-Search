# For stitching together our grid of images from the microscope
# We should try this file with/without preprocessing from background & shading correction
# We will use multiview_stitcher

# We will need the translation offset (positions) or each tile
# I think images can be given in any numpy compatible array

# TODO: When gathering images, can we save the servo positions at each capture somehow then load it in this file?
# We only have 2D layout, but this can be used if the Z-axis is ever added to the system

