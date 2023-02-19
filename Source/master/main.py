import RPi.GPIO as GPIO
import utils
from uart_messenger import UART_Messenger
import threading

# GPIO setup
GPIO.setmode(GPIO.BCM)
reset_pin = 23
GPIO.setup(reset_pin, GPIO.OUT)

# Creating arduino comms instance
slave = UART_Messenger('/dev/ttyAMA1', 115200, timeout=1, reset_pin=reset_pin)

# Sending a reset_signal to the arduino
print("Waiting before reset")
status = slave.send_reset()
if status != 0: exit()

# Waiting till connection is stablished
status = slave.wait_for_connection()
if status != 0: exit()

# Unit testing the components
x = threading.Thread(target=utils.steering_test, args=(slave,))
x.start()

while True:
    slave.fetch_msg()
