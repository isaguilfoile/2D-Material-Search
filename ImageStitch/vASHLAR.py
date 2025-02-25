"""
https://github.com/labsyspharm/ashlar
https://labsyspharm.github.io/ashlar/
"""

"""
https://github.com/yfukai/m2stitch
https://m2stitch.readthedocs.io/en/latest/
"""

import os
import cv2
import numpy as np
from typing import List, Tuple

def save_image_grid(image_grid: List[List[np.ndarray]], output_dir: str):
    """
    Saves images in a format suitable for M2Stitch (row-wise stitching first).
    """

    for row_idx, row in enumerate(image_grid):
        row_dir = os.path.join(output_dir, f"row_{row_idx}")
        os.makedirs(row_dir, exist_ok=True)

        for col_idx, img in enumerate(row):
            if img is not None:
                cv2.imwrite(os.path.join(row_dir, f"image_{col_idx}.jpg"), img)

    print(f"Images saved in {output_dir}. Use M2Stitch to stitch each row, the stitch rows together")

