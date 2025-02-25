"""
This tool can be used to identify numbers in images
"""

import cv2
import pytesseract
import numpy as np
from typing import List, Tuple

class ImageData:
    """
    Stores both an image and extracted numbers.
    """
    def __init__(self, image: np.ndarray, numbers: List[int], position: Tuple[int, int] = None):
        self.image = image
        self.numbers = numbers
        self.position = position # (row, col) in the final grid layout

def extract_numbers_from_image(image: np.ndarray) -> List[int]:
    """
    Extracts numbers from an image using OpenCV and Tesseract OCR.
    Returns a list of of numbers present in the image.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    # Detect text using Tesseract
    custom_config = r'--oem 3 --psm 6 outputbase digits'
    detected_text = pytesseract.image_to_string(thresh, config=custom_config)

    # Extract numbers
    numbers = [int(num) for num in detected_text.split() if num.isdigit()]
    return numbers

def process_images(image_paths: List[str]) -> List[ImageData]:
    """
    Processes a list of image paths, extracts numbers, and and associates them with image data
    """

    processed_images = []

    for path in image_paths:
        image = cv2.imread(path)
        numbers = extract_numbers_from_image(image)
        processed_images.append(ImageData(image, numbers))

    return processed_images