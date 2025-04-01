"""
This tool uses the numbers found images to find sub-image neighbors and construct
a layout (2D array) of images to prep for stitching.
"""

from NumFinder import *
from typing import Dict

def determine_positions(images: List[ImageData]) -> Dict[Tuple[int, int], ImageData]:
    """
    Determines the positions of images based on their numbered markers.
    """
    position_map = {}
    visited = set()

    # Choose a reference image to start
    start_image = images[0]
    start_image.position = (0, 0)
    position_map[(0, 0)] = start_image
    visited.add(tuple(start_image.numbers))

    # Process images iteratively
    to_process = [start_image]

    while to_process:
        current_image = to_process.pop(0)
        row, col = current_image.position

        for img in images:
            if img.position is not None or tuple(img.numbers) in visited:
                continue

            # Determine if the image is above
            if any (num + 1 in current_image.numbers for num in img.numbers):
                img.position = (row - 1, col)
            # Determine if image is below
            elif any (num + 1 in current_image.numbers for num in img.numbers):
                img.position = (row + 1, col)
            # Determine if the image is to the right
            elif any (num - 10 in current_image.numbers for num in img.numbers):
                img.position = (row, col + 1)
            # Determine if the image is to the left
            elif any (num + 10 in current_image.numbers for num in img.numbers):
                img.position = (row, col - 1)
            else:
                continue

            position_map[img.position] = img
            visited.add(tuple(img.numbers))
            to_process.append(img)

    return position_map