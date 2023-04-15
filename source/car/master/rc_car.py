import RPi.GPIO as GPIO
import utils
import threading
import time
import struct
import sys
import select
from picamera2 import Picamera2
import cv2
import math

sys.path.insert(1, "/home/jp/Projects/smart-4g-rc-car/source/common")
from socket_relay_client import RelayClientUDP
from mqtt_client import MQTT_Client
from uart_messenger import UART_Messenger

class RC_Car:
    def __init__(self, uart_path, uart_baudrate, slave_reset_pin, controller_path, remote_host, remote_port):
        # GPIO setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(slave_reset_pin, GPIO.OUT)

        # Creating arduino comms instance
        self.slave = UART_Messenger(uart_path, uart_baudrate, timeout=1, reset_pin=slave_reset_pin)
        #if not self.car_setup(): exit()

        # Worker thread to fetch commands and send them to arduino
        #self.command_worker_thread = threading.Thread(target=self.slave.command_worker, daemon=True)
        #self.command_worker_thread.start()
        
        # Worker to fetch msg from arduino and send them to respective queues
        self.message_worker_thread = threading.Thread(target=self.slave.message_worker, daemon=True)
        self.message_worker_thread.start()
        
        # Initializing the camera
        self.cam = Picamera2()
        config = self.cam.create_preview_configuration(main={"size": (640, 480), "format":"RGB888"}, lores={"size": (320, 240), "format": "YUV420"})#, controls={"FrameDurationLimits": (16666, 16666)})
        self.cam.configure(config)
        
        # Client for socket relay
        self.remote_controller = RelayClientUDP(remote_host, remote_port)
        self.remote_controller.sendto("OK".encode())
        self.relay_host = remote_host
        self.relay_port = remote_port
        
    def main_loop(self):
        self.cam.start()
        while True:
            # Send a new frame to the remote controller
            self.send_encoded_frame()
            
            # Fetch any commands received
            data, address = self.remote_controller.recvfrom(128)
            if not data: continue
            
            #self.slave.send_command(data, encoded=True)
                
    def send_encoded_frame(self):
        frame = self.cam.capture_array("main")
    
        # Encoding and serializing the frame
        result, encoded_frame = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY),80])
        buffer = encoded_frame.tobytes()
        size = len(buffer)
        
        # Sending the serialized frame through the socket in chunks
        max_datagram_size = 4064
        packets = math.ceil(size / max_datagram_size)
        self.remote_controller.sendto(packets.to_bytes(4, byteorder="big"))
        print(f"{packets} packets")
        
        for i in range(packets):
            data = buffer[i*(max_datagram_size):(i+1)*(max_datagram_size)]
            print(f"sending {len(data)} bytes")
            self.remote_controller.sendto(data)

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
                 controller_path="auto",
                 remote_host="3.134.62.14",
                 remote_port=8485)
    
    car.main_loop()
    
    
    