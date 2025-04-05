# from ConexCC import ConexCC

# if __name__ == "__main__":
#     ConexCC.dump_possible_states()
#     motor_x = ConexCC(com_port='com5', velocity=0.5, max_velocity=0.4, dev=1) # TODO: We might have to analyze ports, why is max velocity less than velocity?
#     ready = motor_x.wait_for_ready(timeout=60)
#     if ready:
#         motor_x.move_absolute(motor_x.max_limit / 2)
#         ready = motor_x.wait_for_ready(timeout=60)
#         if ready:
#             motor_x.move_relative(-3)
#             ready = motor_x.wait_for_ready(timeout=60)
#             if ready:
#                 print('ok!')
#             else:
#                 print('not ok 2!')
#         else:
#             print('not ok 1!')
#         motor_x.close()
#     else:
#         print('something went wrong')

import time
from ConexCC import ConexCC
from ImageCapture import DirectShowCam
import os

import sys  # Import sys to exit the script

# Ensure that the image output directory exists before running
output_dir = "MotorMover/images"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

if __name__ == '__main__':
    WAFERSIZE = 2  # Define the wafer size limit TODO Add auto ranging

    # Check if WAFERSIZE is within the valid range
    if not (0 <= WAFERSIZE <= 12):
        print("Error: WAFERSIZE must be between 0 and 12.")
        sys.exit(1)  # Exit with an error code

    # Create Camera instance
    camera = DirectShowCam(camera_index=0)

    ConexCC.dump_possible_states()
    conex_X = ConexCC(com_port='com4', velocity=0.5, dev=1)

    if conex_X.wait_for_ready(timeout=60):
        if conex_X.moveOut(WAFERSIZE): #TODO add FRAMESIZE to arg if we want to call getPic here, and then Y.moveOut(FRAMESIZE)
            time.sleep(1)  # Wait 1 second at max position
            #conex_Y.moveOut() #TODO use STEPSIZE in ConexCC to move down one
            conex_X.moveIn(WAFERSIZE)

        print("Completed movement sequence.")
        conex_X.close()
    else:
        print("Controller not ready!")
