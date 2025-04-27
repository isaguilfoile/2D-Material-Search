import time
from ConexCC import ConexCC
from ImageCapture import DirectShowCam, find_available_cameras
from SlideAlign import center_of_frame
import os
import cv2

import msvcrt

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
            positions.append([round(x, 10), round(y, 10)])  # rounding to avoid floating point weirdness

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
    camera = DirectShowCam(camera_index=1, directory=output_dir)

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

    def offset_locations(offset_x, offset_y, index):
        global locations

        for i in range(index, len(locations)):
            locations[i][0] += offset_x
            locations[i][1] += offset_y
    
    def fine_tune_start(conex_X, conex_Y, camera, step_size=0.01):
        """
        Fine-tune the starting motor positions using arrow keys, with live camera view.
        Arrow keys move the stage in small increments.
        Non-arrow key exits fine-tuning.

        Args:
            conex_X: ConexCC instance controlling X axis
            conex_Y: ConexCC instance controlling Y axis
            camera: DirectShowCam instance
            step_size: Movement increment in mm

        Returns:
            (total_dx, total_dy): Total distance traveled during fine-tuning
        """

        total_dx = 0.0
        total_dy = 0.0

        print("\nFine-tuning mode:")
        print("Use arrow keys to move the stage.")
        print("Press any non-arrow key to exit fine-tuning.\n")

        cv2.namedWindow("Fine-tune view", cv2.WINDOW_NORMAL)

        while True:
            frame = camera.get_frame()
            cv2.imshow("Fine-tune view", frame)

            # Check if a key has been pressed
            if msvcrt.kbhit():
                key = msvcrt.getch()

                if key == b'\x00':  # Arrow key prefix
                    arrow = msvcrt.getch()
                    if arrow == b'H':  # Up
                        conex_Y.move_relative(step_size)
                        total_dy += step_size
                        print(f"Moved +Y by {step_size} mm")
                    elif arrow == b'P':  # Down
                        conex_Y.move_relative(-step_size)
                        total_dy -= step_size
                        print(f"Moved -Y by {step_size} mm")
                    elif arrow == b'K':  # Left
                        conex_X.move_relative(-step_size)
                        total_dx -= step_size
                        print(f"Moved -X by {step_size} mm")
                    elif arrow == b'M':  # Right
                        conex_X.move_relative(step_size)
                        total_dx += step_size
                        print(f"Moved +X by {step_size} mm")
                else:
                    print("Exiting fine-tuning.")
                    break

            # Refresh at a reasonable rate
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyWindow("Fine-tune view")

        return total_dx, total_dy
        
    o_x, o_y, = fine_tune_start(conex_X, conex_Y, camera)
    offset_locations(o_x, o_y, 0)

    for index, location in enumerate(locations):
        conex_X.move_absolute(location[0])
        conex_Y.move_absolute(location[1])
        time.sleep(8)
        # take_picture()
        camera.capture_frame("tmp.jpg")
        o_x, o_y = center_of_frame("images/raw/tmp.jpg")
        o_x = -1 * o_x
        o_y = -1 * o_y
        print(o_x, o_y)

        offset_locations(o_x, o_y, index) # Fix upcoming positions

        conex_X.move_relative(o_x)
        conex_Y.move_relative(o_y)
        time.sleep(3)
        take_picture()

    conex_X.close()
    conex_Y.close()

    camera.close()
    camera.save_table("files", "image_dt.csv") # Save table containing image names and locations
    
