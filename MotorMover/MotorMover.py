import time
from ConexCC import ConexCC
from ImageCapture import DirectShowCam, find_available_cameras
import os

import sys  # Import sys to exit the script

output_dir = "images/raw/"

if __name__ == '__main__':
    WAFER_SIZE = 0.5  # Define the wafer size limit TODO Add auto ranging
    STEP_SIZE = 0.05 # TODO Figure out the desired step size

    # Check if WAFER SIZE is within the valid range
    if not (0 <= WAFER_SIZE <= 12):
        print("Error: WAFERSIZE must be between 0 and 12.")
        sys.exit(1)  # Exit with an error code

    # Create Camera instance
    camera = DirectShowCam(camera_index=0, directory=output_dir)

    ConexCC.dump_possible_states()
    conex_X = ConexCC(com_port='com5', velocity=0.5, dev=1)
    conex_Y = ConexCC(com_port='com6', velocity=0.5, dev=1)

    if conex_X.wait_for_ready(timeout=60) and conex_Y.wait_for_ready(timeout=60):
        conex_X.goHome()
        conex_Y.goHome()

    image_counter = 0  # Counter for naming images

    def take_picture():
        """
        Save a photo and update the image table. This should be called at every stage position
        """
        image_name = f"{image_counter:02d}.jpg"
        camera.document_frame(image_name, conex_X.cur_pos, conex_Y.cur_pos, 0)
        image_counter += 1
    
    take_picture() # Take picture at home location (0, 0)
    while conex_Y.cur_pos < WAFER_SIZE:
        while conex_X.cur_pos < WAFER_SIZE:
            conex_X.move_relative(STEP_SIZE)
            take_picture()
        conex_Y.move_relative(STEP_SIZE)
        take_picture()
        while conex_X.cur_pos > 0:
            conex_X.move_relative(-1 * STEP_SIZE)
            take_picture()
        conex_Y.move_relative(STEP_SIZE)

    camera.close()
    camera.save_table("files", "image_dt.csv") # Save table containing image names and locations
    
