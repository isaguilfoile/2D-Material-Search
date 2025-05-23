import time
import os
import sys
import threading
import msvcrt
import cv2

from ConexCC import ConexCC
from ImageCapture import DirectShowCam, find_available_cameras
from SlideAlign import center_of_frame

output_dir = "images/raw/"

def snake_positions(x_0, x_n, y_0, y_n, delta, num_steps):
    positions = []
    
    # Handle step direction properly
    x_direction = 1 if x_n >= x_0 else -1
    y_direction = 1 if y_n >= y_0 else -1

    # Compute ranges using float-compatible arange logic
    def float_range(start, stop, step):
        # num_steps = int(abs((stop - start) / step)) + 1
        return [start + i * step for i in range(num_steps)]

    x_vals = float_range(x_0, x_n, delta * x_direction)
    y_vals = float_range(y_0, y_n, delta * y_direction)

    for idx, y in enumerate(y_vals):
        row = x_vals if idx % 2 == 0 else x_vals[::-1]
        for x in row:
            positions.append([x, y])  # rounding to avoid floating point weirdness

    return positions

def live_camera_view(camera, conex_X, conex_Y, stop_event):
    cv2.namedWindow("Live View", cv2.WINDOW_NORMAL)
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    color = (0, 255, 0)
    thickness = 1

    while not stop_event.is_set():
        frame = camera.get_frame()

        # Overlay motor positions
        pos_text = f"X: {conex_X.cur_pos:.3f} mm | Y: {conex_Y.cur_pos:.3f} mm"
        cv2.putText(frame, pos_text, (10, 30), font, font_scale, color, thickness, cv2.LINE_AA)

        cv2.imshow("Live View", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            stop_event.set()
            break

    cv2.destroyWindow("Live View")

def take_picture(camera, image_counter, conex_X, conex_Y):
    """
    Save a photo and update the image table. This should be called at every stage position.
    """
    image_name = f"{image_counter:03d}.jpg"
    camera.document_frame(image_name, conex_X.cur_pos, conex_Y.cur_pos, 0)
    return image_counter + 1

def offset_locations(offset_x, offset_y, locations, index):
    for i in range(index, len(locations)):
        locations[i][0] += offset_x
        locations[i][1] += offset_y

def fine_tune_start(conex_X, conex_Y, step_size=0.01):
    """
    Fine-tune the starting motor positions using arrow keys.
    """
    total_dx = 0.0
    total_dy = 0.0

    print("\nFine-tuning mode:")
    print("Use arrow keys to move the stage.")
    print("Press any non-arrow key to exit fine-tuning.\n")

    while True:
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

        time.sleep(0.05)  # prevent high CPU usage

    return total_dx, total_dy

def motor_move(conex_X, conex_Y, locations, image_counter, camera: DirectShowCam):

    WAFER_SIZE = 0.64  # Define the wafer size limit
    STEP_SIZE = 0.16   # Step size in mm

    if not (0 <= WAFER_SIZE <= 12):
        print("Error: WAFER_SIZE must be between 0 and 12.")
        sys.exit(1)

    print(f"Conex X: {conex_X.cur_pos}")
    print(f"Conex Y: {conex_Y.cur_pos}")
    print(f"Set Loc: {locations}")

    for index, location in enumerate(locations):
        print(f"Conex X bef: {conex_X.cur_pos}")
        print(f"Conex Y bef: {conex_Y.cur_pos}")
        conex_X.move_absolute(location[0])
        conex_Y.move_absolute(location[1])
        print(f"Conex X: {conex_X.cur_pos}")
        print(f"Conex Y: {conex_Y.cur_pos}")
        time.sleep(0.1)
        print("inside:,", conex_X.cur_pos, conex_Y.cur_pos)
        camera.capture_frame("tmp.jpg")
        offset_x, offset_y = center_of_frame("images/raw/tmp.jpg")
        offset_x = -offset_x
        print(f"Centering correction: ({offset_x:.4f}, {offset_y:.4f})")

        offset_locations(offset_x, offset_y, locations, index)

        conex_X.move_relative(offset_x)
        conex_Y.move_relative(offset_y)
        time.sleep(0.1)

        image_counter = take_picture(camera, image_counter, conex_X, conex_Y)
