import pytesseract
import cv2
from math import sqrt

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract'

# Load image
image_path = "ImageStitch/microscope_images/01.jpg"
image = cv2.imread(image_path)
rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Configure pytesseract to detect only numbers
options = "outputbase digits"

# Get image center
height, width, _ = rgb.shape
center_x, center_y = width // 2, height // 2

# Run OCR
data = pytesseract.image_to_data(rgb, config=options, output_type=pytesseract.Output.DICT)

# Store results
distances = {}

for i in range(len(data['text'])):
    text = data['text'][i].strip()
    if text.isdigit():
        x = data['left'][i]
        y = data['top'][i]
        w = data['width'][i]
        h = data['height'][i]
        text_center_x = x + w // 2
        text_center_y = y + h // 2
        distance = sqrt((text_center_x - center_x)**2 + (text_center_y - center_y)**2)
        distances[text] = round(distance, 2)

# Output distances
for number, dist in distances.items():
    print(f"Distance from center to '{number}': {dist} pixels")