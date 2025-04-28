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
            positions.append([round(x, 2), round(y, 2)])  # rounding to avoid floating point weirdness

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

if __name__ == '__main__':
    image_counter = 0

    WAFER_SIZE = 0.64  # Define the wafer size limit
    STEP_SIZE = 0.16   # Step size in mm

    START_X = 11.5
    END_X = 0
    START_Y = 11.5
    END_Y = 0

    F_END_X = 6.25
    F_END_Y = 6.25

    if not (0 <= WAFER_SIZE <= 12):
        print("Error: WAFER_SIZE must be between 0 and 12.")
        sys.exit(1)

    locations = []
    big_locations = snake_positions(START_X, F_END_X, START_Y, F_END_Y, 1.05, 6)
    for local in big_locations:
        START_X = round(local[0], 2)
        START_Y = round(local[1], 2)
        END_X = round((START_X - 0.64), 2)
        END_Y = round((START_Y - 0.64), 2)
        temp = snake_positions(START_X, END_X, START_Y, END_Y, 0.16, 5)
        for place in temp:
            locations.append(place)

    # print(locations, len(locations))
    print(len(big_locations))

    camera = DirectShowCam(camera_index=1, directory=output_dir)

    ConexCC.dump_possible_states()
    conex_X = ConexCC(com_port='com5', velocity=0.5, dev=1)
    conex_Y = ConexCC(com_port='com6', velocity=0.5, dev=1)

    if conex_X.wait_for_ready(timeout=60) and conex_Y.wait_for_ready(timeout=60):
        conex_X.move_absolute(11.5)
        conex_Y.move_absolute(11.5)

    # Start live camera thread
    stop_event = threading.Event()
    camera_thread = threading.Thread(target=live_camera_view, args=(camera, conex_X, conex_Y, stop_event))
    camera_thread.start()

    # Fine-tune starting position
    o_x, o_y = fine_tune_start(conex_X, conex_Y)
    offset_locations(o_x, o_y, locations, 0)

    for index, location in enumerate(locations):
        conex_X.move_absolute(location[0])
        conex_Y.move_absolute(location[1])
        time.sleep(0.1)

        camera.capture_frame("tmp.jpg")
        offset_x, offset_y = center_of_frame("images/raw/tmp.jpg")
        offset_x = -offset_x
        # offset_y = -offset_y
        print(f"Centering correction: ({offset_x:.4f}, {offset_y:.4f})")

        offset_locations(offset_x, offset_y, locations, index)

        conex_X.move_relative(offset_x)
        conex_Y.move_relative(offset_y)
        time.sleep(0.1)

        image_counter = take_picture(camera, image_counter, conex_X, conex_Y)

    # Close everything
    conex_X.close()
    conex_Y.close()
    camera.close()
    camera.save_table("files", "image_dt.csv")

    # Stop live camera thread
    stop_event.set()
    camera_thread.join()
