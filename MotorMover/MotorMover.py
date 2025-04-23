import time
from ConexCC import ConexCC
from ImageCapture import DirectShowCam, find_available_cameras
import os

import sys  # Import sys to exit the script

output_dir = "images/raw/"

def snake_positions(x_0, x_n, y_0, y_n, delta):
    positions = []
    
    # Handle step direction properly
    x_direction = 1 if x_n >= x_0 else -1
    y_direction = 1 if y_n >= y_0 else -1

    # Compute ranges using float-compatible arange logic
    def float_range(start, stop, step):
        num_steps = int(abs((stop - start) / step)) + 1
        return [start + i * step for i in range(num_steps)]

    x_vals = float_range(x_0, x_n, delta * x_direction)
    y_vals = float_range(y_0, y_n, delta * y_direction)

    for idx, y in enumerate(y_vals):
        row = x_vals if idx % 2 == 0 else x_vals[::-1]
        for x in row:
            positions.append((round(x, 10), round(y, 10)))  # rounding to avoid floating point weirdness

    return positions

if __name__ == '__main__':
    image_counter = 0

    WAFER_SIZE = 0.64  # Define the wafer size limit TODO Add auto ranging
    STEP_SIZE = 0.16 # TODO Figure out the desired step size

    START_X = 12
    END_X = 11.36

    START_Y = 12
    END_Y = 11.36

    locations = snake_positions(START_X, END_X, START_Y, END_Y, STEP_SIZE)
    print(locations)

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
        conex_X.move_absolute(12)
        conex_Y.move_absolute(12)

    image_counter = 0  # Counter for naming images

    def take_picture():
        """
        Save a photo and update the image table. This should be called at every stage position
        """
        global image_counter

        image_name = f"{image_counter:02d}.jpg"
        camera.document_frame(image_name, conex_X.cur_pos, conex_Y.cur_pos, 0)
        image_counter += 1

    for location in locations:
        conex_X.move_absolute(location[0])
        conex_Y.move_absolute(location[1])
        time.sleep(8)
        take_picture()

    conex_X.close()
    conex_Y.close()

    camera.close()
    camera.save_table("files", "image_dt.csv") # Save table containing image names and locations
    
