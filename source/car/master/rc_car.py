import RPi.GPIO as GPIO
import utils
import threading
from multiprocessing import Process
import time
import sys

sys.path.insert(1, "/home/jp/Projects/smart-4g-rc-car/source/common")
from socket_relay_client import RelayClientUDP
from mqtt_client import MQTT_Client
from uart_messenger import UART_Messenger
from video_streamer import Video_Streamer

class RC_Car:
    def __init__(self, uart_path, uart_baudrate, slave_reset_pin, controller_path, remote_host, remote_control_port, remote_video_port):
        # GPIO setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(slave_reset_pin, GPIO.OUT)
        
        # Client for mqtt broker
        #self.mqtt_client = MQTT_Client()
        #self.mqtt_client.connect(remote_host)
        #self.mqtt_client.loop_start()

        # Creating arduino comms instance
        self.slave = UART_Messenger(uart_path, uart_baudrate, timeout=1, reset_pin=slave_reset_pin, mqtt_client=None)
        if not self.car_setup(): exit()
        
        # Applying initial settings file
        #self.slave.send_command("IC")
        #self.slave.send_command("FC")
        
        # Worker to fetch msg from arduino and process accordingly
        message_worker_thread = threading.Thread(target=self.slave.message_worker, daemon=True)
        message_worker_thread.start()
        
        # Control client for socket relay
        print("Connecting to main relay")
        self.remote_controller = RelayClientUDP(remote_host, remote_control_port)
        self.remote_controller.sendto("OK".encode())
        self.control_relay_host = remote_host
        self.control_relay_port = remote_control_port
        
        # Video client process
        self.video_streamer = Video_Streamer(remote_host, remote_video_port)
        self.video_stream = Process(target=self.video_streamer.start, daemon=True)
        self.video_stream.start()
        
    def main_loop(self):
        while True:
            # Send a new frame to the remote controller
            #self.send_encoded_frame()
            
            # Fetch any commands received
            data, address = self.remote_controller.recvfrom(1024)
            if not data: continue
            
            self.slave.send_command(data, encoded=True)

    def car_setup(self):
        # Sending a reset_signal to the arduino
        print("Resetting slave")
        ret = self.slave.send_reset()
        if not ret:
            print("Something went wrong, exiting...")
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
                 controller_path="auto",
                 remote_host="3.134.62.14",
                 remote_control_port=8485,
                 remote_video_port=8487)
    
    try:
        car.main_loop()
        
    except KeyboardInterrupt:
        GPIO.cleanup()
    
    
    