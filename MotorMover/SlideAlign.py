import pytesseract
import cv2
from math import sqrt

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract'

def connect_numbers():
    # Load image
    image_path = "images/raw/tmp.jpg"
    image = cv2.imread(image_path)
    print(image.shape)
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

    # Draw a copy of the original image
    output_img = image.copy()

    for i in range(len(data['text'])):
        text = data['text'][i].strip()
        if text.isdigit() and (len(text) == 2):
            x = data['left'][i]
            y = data['top'][i]
            w = data['width'][i]
            h = data['height'][i]
            text_center_x = x + w // 2
            text_center_y = y + h // 2
            distance = sqrt((text_center_x - center_x)**2 + (text_center_y - center_y)**2)
            distances[text] = round(distance, 2)

            # Draw a line from center to the text center
            cv2.line(output_img, (center_x, center_y), (text_center_x, text_center_y), (0, 255, 0), 2)

            # Put distance text near the line (shift a bit for better visibility)
            label_x = (center_x + text_center_x) // 2
            label_y = (center_y + text_center_y) // 2
            cv2.putText(output_img, f"{distances[text]}px", (label_x + 5, label_y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    # Draw the center point
    cv2.circle(output_img, (center_x, center_y), 5, (255, 0, 0), -1)

    # Resize image for display if it's too large
    max_width = 1200  # pixels
    scale = 1.0
    if output_img.shape[1] > max_width:
        scale = max_width / output_img.shape[1]
        output_img = cv2.resize(output_img, (0, 0), fx=scale, fy=scale)

    # Show image
    cv2.imshow("Detected Numbers with Distances", output_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def center_of_frame(image_path, debug=False):
    # Load image
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
    coordinates = []

    if (debug):
        print(data['text'])

    num_count = 0
    for i in range(len(data['text'])):
        text = data['text'][i].strip()
        if text.isdigit() and (len(text) == 2):
            num_count += 1

    if (num_count == 4):
        for i in range(len(data['text'])):
            text = data['text'][i].strip()
            if text.isdigit() and (len(text) == 2):
                x = data['left'][i]
                y = data['top'][i]
                w = data['width'][i]
                h = data['height'][i]
                text_center_x = x + w // 2
                text_center_y = y + h // 2
                coordinates.append((text_center_x, text_center_y))

        center_x_pixel = 0
        center_y_pixel = 0
        for num_center in coordinates:
            center_x_pixel += num_center[0]
            center_y_pixel += num_center[1]

        center_x_pixel = round(center_x_pixel / 4)
        center_y_pixel = round(center_y_pixel / 4)

        offset_x = (center_x_pixel - center_x) * (1/21600)
        offset_y = (center_y_pixel - center_y) * (1/21600)
    else:
        offset_x = 0
        offset_y = 0

    if (debug):
        output_img = image.copy()
        
        for coordinate in coordinates:
            cv2.circle(output_img, (coordinate[0], coordinate[1]), 10, (0, 255, 0), -1)

        # Draw the center point
        print(center_x_pixel, center_y_pixel)
        cv2.circle(output_img, (center_x_pixel, center_y_pixel), 15, (255, 0, 0), -1)


        # Resize image for display if it's too large
        max_width = 1200  # pixels
        scale = 1.0
        if output_img.shape[1] > max_width:
            scale = max_width / output_img.shape[1]
            output_img = cv2.resize(output_img, (0, 0), fx=scale, fy=scale)

        # Show image
        cv2.imshow("Detected Numbers with Distances", output_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return (offset_x, offset_y) # Offset distance in micro meters

if __name__ == "__main__":
    print(center_of_frame("images/raw/06.jpg", debug=False))