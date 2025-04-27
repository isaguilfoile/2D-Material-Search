# This file is responsible for capturing images from the EXCELIS 4K Accu-Scope camera
# The goal is to automate image capturing while the stage controllers are iterating through positions

import cv2
import os
import pandas as pd

def find_available_cameras(max_index=10):
    """
    Scans for available camera indices to pass to DirectShowCam Class
    """

    available_cameras = []

    for index in range(max_index):
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW) # Use DirectShow
        if cap.isOpened():
            available_cameras.append(index)
            cap.release()

    return available_cameras

class DirectShowCam:

    def __init__(self, camera_index, directory):
        self.index = camera_index
        self.save_directory = directory
        self.data_table = pd.DataFrame(columns=["Image Name", "X Position", "Y Position", "Z Position"])
        # Initialize the camera
        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)

        if not self.cap.isOpened():
            print("Error: Could not open the camera")

        # Ensure that the image output directory exists before running
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Delete all files in directory before saving new images
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                os.remove(file_path)

    def get_frame(self):
        """Grab a frame and return it as a numpy array (BGR)."""
        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("Failed to capture frame from camera.")
        return frame

        
    def capture_frame(self, file_name):
        """ Take an image WITHOUT appending it to the image location table """
        # Ensure that save directory exists
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory, exist_ok=True);

        # Capture a single frame (image) and save
        ret, frame = self.cap.read()
        
        if not ret:
            print("Error: failed to capture image")
            self.cap.release()
            return False
        
        file_path = os.path.join(self.save_directory, file_name)
        cv2.imwrite(file_path, frame)

        return True
    
    def document_frame(self, file_name, x_pos, y_pos, z_pos):
        """ Take an image and append its location to the image table """
        self.capture_frame(file_name) # Take image and save

        self.data_table.loc[-1] = [file_name, x_pos, y_pos, z_pos]
        self.data_table.index += 1
        self.data_table.sort_index()

        return True
    
    def save_table(self, directory, file_name):
        """ Saves image data table to a csv file """
        if not os.path.exists(directory):
            os.makedirs(directory)

        file_path = os.path.join(directory, file_name)
        self.data_table.to_csv(file_path, index=False)
        print(f"Data table saved to {file_path}")


    def close(self):
        # De-initialize the camera
        self.cap.release()
        cv2.destroyAllWindows()

        return True

if __name__ == "__main__":
    print(find_available_cameras())
    # Create and initialize camera
    camera = DirectShowCam(camera_index=1, directory="MotorMover/CameraTest")
    camera.document_frame("test1.jpg", 1, 2, 0)
    image1 = cv2.imread("MotorMover/CameraTest/test1.jpg")
    print(image1.shape)
    camera.document_frame("test2.jpg", 5, 6, 0)
    camera.save_table("files", "test.csv")
    camera.close()
