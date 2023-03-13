import RPi.GPIO as GPIO
import utils
from uart_messenger import UART_Messenger
from remote_controller import RemoteController
import threading
import time

def car_setup():
    # Sending a reset_signal to the arduino
    print("Resetting slave")
    ret = slave.send_reset()
    if not ret:
        print("Something went wrong, exitting...")
        return False

    # Waiting till connection is stablished
    print("Attempting UART connection with slave")
    ret = slave.wait_for_connection(timeout=5)
    if not ret:
        print("Timeout reached, could not stablish connection with slave!")
        return False
        
    # Waiting for the slave to initialize all car components
    print("Waiting for all components to be initialized by slave...")
    ret = slave.wait_for_message("ready", timeout=10)
    if not ret:
        print("Timeout reached, looks like some components are not initializing...")
        return False
        
    time.sleep(3)
    slave.flushInput()
    print("Setup successfull! Slave ready to receive commands...")
    return True

# GPIO setup
GPIO.setmode(GPIO.BCM)
reset_pin = 23
GPIO.setup(reset_pin, GPIO.OUT)

# Creating arduino comms instance
slave = UART_Messenger('/dev/ttyAMA1', 115200, timeout=1, reset_pin=reset_pin)
if not car_setup(): exit()
    
# Remote controller thread
print("Starting connection with remote controller")
controller = RemoteController("/dev/input/event0", slave)
control_thread = threading.Thread(target=controller.read_loop, daemon=True)
control_thread.start()
print("Remote controller active")

while True:
    try:
        slave.fetch_msg()
    except Exception as e:
        print("Could not fetch message: " + str(e))
