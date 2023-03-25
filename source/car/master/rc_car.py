import RPi.GPIO as GPIO
import utils
from uart_messenger import UART_Messenger
from remote_controller import RemoteController
import threading
import time
import struct

class RC_Car:
    def __init__(self, uart_path, uart_baudrate, slave_reset_pin, controller_path):
        # GPIO setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(slave_reset_pin, GPIO.OUT)

        # Creating arduino comms instance
        self.slave = UART_Messenger(uart_path, uart_baudrate, timeout=1, reset_pin=slave_reset_pin)
        if not self.car_setup(): exit()

        # Worker thread to fetch commands and send them to arduino
        self.command_worker_thread = threading.Thread(target=self.slave.command_worker, daemon=True)
        self.command_worker_thread.start()
        
        # Worker to fetch msg from arduino and send them to respective queues
        self.message_worker_thread = threading.Thread(target=self.slave.message_worker, daemon=True)
        self.message_worker_thread.start()
            
        # Remote controller thread
        print("Starting connection with remote controller")
        self.controller = RemoteController(controller_path, self.slave)
        self.control_thread = threading.Thread(target=self.controller.read_loop, daemon=True)
        self.control_thread.start()
        print("Remote controller active")
        
    def main_loop(self):
        while True:
            '''try:
                self.slave.fetch_msg()
            except Exception as e:
                print("Could not fetch message: " + str(e))'''
            if not self.slave.msg_queues[0x00].empty():
                msg = struct.unpack("<f", self.slave.msg_queues[0x00].get())
                print(f"RPM-> {msg}")

    def car_setup(self):
        # Sending a reset_signal to the arduino
        print("Resetting slave")
        ret = self.slave.send_reset()
        if not ret:
            print("Something went wrong, exitting...")
            return False

        # Waiting till connection is stablished
        print("Attempting UART connection with slave")
        ret = self.slave.wait_for_connection(timeout=5)
        if not ret:
            print("Timeout reached, could not stablish connection with slave!")
            return False
            
        # Waiting for the slave to initialize all car components
        print("Waiting for all components to be initialized by slave...")
        ret = self.slave.wait_for_message("ready", timeout=10)
        if not ret:
            print("Timeout reached, looks like some components are not initializing...")
            return False
            
        time.sleep(3)
        self.slave.flushInput()
        print("Setup successfull! Slave ready to receive commands...")
        return True
    
if __name__ == "__main__":
    car = RC_Car(uart_path='/dev/ttyAMA1',
                 uart_baudrate=115200,
                 slave_reset_pin=23,
                 controller_path="auto")
    
    car.main_loop()
    
    
    