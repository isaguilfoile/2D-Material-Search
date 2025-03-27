#============================================================
# Initialization Start 
# The script within Initialization Start and Initialization End is needed for properly  
# initializing Command Interface for CONEX-CC instrument. 
# The user should copy this code as is and specify correct paths here. 

import sys
import clr
import time

# Command Interface DLL can be found here.
print("Adding location of Newport.CONEXCC.CommandInterface.dll to sys.path")
sys.path.append(r'C:\Program Files\Newport\MotionControl\CONEX-CC\Bin')
sys.path.append(r'C:\Program Files (x86)\Newport\MotionControl\CONEX-CC\Bin')

# Add reference to assembly and import names from namespace
clr.AddReferenceToFile("Newport.CONEXCC.CommandInterface.dll")
from CommandInterface import *

#============================================================
# Instrument Initialization
instrument = "COM25"
print(f'Instrument Key => {instrument}')

# Create a device instance and open communication with the instrument
CC = ConexCC()
ret = CC.OpenInstrument(instrument)
print(f'OpenInstrument => {ret}')

# Get positive software limit
result, response, errString = CC.SR_Get(1)
if result == 0:
    print(f'Positive software limit => {response}')
else:
    print(f'Error => {errString}')

# Get negative software limit
result, response, errString = CC.SL_Get(1)
if result == 0:
    print(f'Negative software limit => {response}')
else:
    print(f'Error => {errString}')

# Get controller revision information
result, response, errString = CC.VE(1)
if result == 0:
    print(f'Controller revision => {response}')
else:
    print(f'Error => {errString}')

# Get current position
result, response, errString = CC.TP(1)
if result == 0:
    print(f'Current position => {response}')
else:
    print(f'Error => {errString}')

#============================================================
# Move the motor to a specific position
target_position = 10.0  # Change this value to your desired position
result, errString = CC.PA_Set(1, target_position)

if result == 0:
    print(f"Motor moving to {target_position} mm")
else:
    print(f"Error moving motor: {errString}")

# Wait for motion to complete
motion_complete = False
while not motion_complete:
    result, response, errString = CC.TP(1)
    if result == 0:
        print(f"Current position: {response} mm")
        if abs(response - target_position) < 0.01:  # Considered reached if within 0.01 mm
            motion_complete = True
    else:
        print(f"Error reading position: {errString}")
    time.sleep(0.5)  # Small delay before checking again

print("Motor has reached the target position.")

# Unregister device
CC.CloseInstrument()
