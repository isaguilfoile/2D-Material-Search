# This file is responsible for capturing images from the EXCELIS 4K Accu-Scope camera
# The goal is to automate image capturing while the stage controllers are iterating through positions

import cv2
import os

class DirectShowCam:

    def __init__(self, camera_index):
        self.index = camera_index
        # Initialize the camera
        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)

        if not self.cap.isOpened():
            print("Error: Could not open the camera")
        
    def capture_frame(self, save_directory, file_name):
        # Ensure that save directory exists
        if not os.path.exists(save_directory):
            os.makedirs(save_directory, exist_ok=True);

        # Capture a single frame (image) and save
        ret, frame = self.cap.read()
        
        if not ret:
            print("Error: failed to capture image")
            self.cap.release()
            return False
        
        file_path = os.path.join(save_directory, file_name)
        cv2.imwrite(file_path, frame)

        return True

    def close(self):
        # De-initialize the camera
        self.cap.release()
        cv2.destroyAllWindows()

        return True

if __name__ == "__main__":
    # Create and initialize camera
    camera = DirectShowCam(camera_index=0)
    camera.capture_frame("MotorMover/CameraTest", "test.jpg")
    camera.close()
