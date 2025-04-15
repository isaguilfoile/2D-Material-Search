import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

def remove_background(img_directory, img_name, dst_directory, dst_name):
    img_path = os.path.join(img_directory, img_name)
    
    img = cv2.imread(img_path, cv2.IMREAD_COLOR)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Use a large Gaussian blur to approximate background
    background = cv2.GaussianBlur(img_gray, (91, 91), 0)
    
    # Subtract the background and normalize
    shadow_removed = cv2.subtract(img_gray, background)
    shadow_removed = cv2.normalize(shadow_removed, None, 0, 255, cv2.NORM_MINMAX)
    
    # (Optional) Enhance contrast using CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(shadow_removed)

    # Display result
    plt.imshow(enhanced, cmap='gray')
    plt.title('Background Removed')
    plt.axis('off')
    plt.show()
    
if __name__ == "__main__":
    remove_background("ImageStitch/ms_images_1", "01.jpg", " ", " ")