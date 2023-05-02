import RPi.GPIO as GPIO
from utils import *
import threading
from multiprocessing import Process
import time
import sys

sys.path.insert(1, "/home/jp/Projects/smart-4g-rc-car/source/common")
from socket_relay_client import RelayClientUDP
from mqtt_client import MQTT_Client
from uart_messenger import UART_Messenger
from video_streamer import Video_Streamer
from sim7600 import SIM7600

class RC_Car:
    def __init__(self, uart_path, uart_baudrate, slave_reset_pin, remote_host, remote_control_port, remote_video_port):
        # GPIO setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(slave_reset_pin, GPIO.OUT)
        
        # Client for mqtt broker
        self.mqtt_client = MQTT_Client()
        self.mqtt_client.will_set(topic="RCCAR-CAR-ON", payload="false", qos=1, retain=True)
        self.mqtt_client.connect(remote_host)
        self.mqtt_client.loop_start()

        # Creating arduino comms instance
        self.slave = UART_Messenger(uart_path, uart_baudrate, timeout=1, reset_pin=slave_reset_pin, mqtt_client=self.mqtt_client)
        self.car_setup()
        
        # Worker to fetch msg from arduino and process accordingly
        message_worker_thread = threading.Thread(target=self.slave.message_worker, daemon=True)
        message_worker_thread.start()
        
        # Applying initial configuration file
        #self.apply_configuration("/home/jp/Projects/smart-4g-rc-car/source/car/config.txt")
        
        # Control client for socket relay
        print("Connecting to main relay")
        self.remote_controller = RelayClientUDP(remote_host, remote_control_port)
        self.remote_controller.sendto("OK".encode())
        self.control_relay_host = remote_host
        self.control_relay_port = remote_control_port
        
        # Video client process
        self.video_streamer = Video_Streamer(remote_host, remote_video_port)
        self.video_stream = threading.Thread(target=self.video_streamer.start, daemon=True)
        self.video_stream.start()
        
        # GPS Position Update
        self.gps = SIM7600("/dev/ttyS0", 115200, power_key=6)
        gps_update_thread = threading.Thread(target=self.gps_update_loop, daemon=True)
        gps_update_thread.start()
        
        self.mqtt_client.publish(topic="RCCAR-CAR-ON", payload="true", qos=1, retain=True)

    def car_setup(self):
        print("Resetting slave")
        self.slave.send_reset()

        print("Attempting UART connection with slave")
        self.slave.wait_for_connection(timeout=5)
            
        print("Waiting for all components to be initialized by slave...")
        self.slave.wait_for_message("ready", timeout=10)
            
        time.sleep(3)
        self.slave.flushInput()
        print("Setup successfull! Slave ready to receive commands...")
        
    def apply_configuration(self, config_file_path):
        commands = get_config_file_commands(config_file_path)
        for command in commands:
            self.slave.send_command(command)
            
    def gps_update_loop(self):
        while True:
            try:
                lat, lon = self.gps.get_gps_coordinates()
                self.mqtt_client.publish(topic="RCCAR-GPS-COORDS", payload=f'{{ "name":"rc-car", "lat":{lat}, "lon":{lon}, "icon":"arrow", "radius":50 }}', qos=1, retain=True)
            except:
                pass
            finally:
                time.sleep(3)
    
    def main_loop(self):
        while True:
            data, address = self.remote_controller.recvfrom(1024)
            if not data: continue
            
            self.slave.send_command(data, encoded=True)
    
if __name__ == "__main__":
    car = RC_Car(uart_path='/dev/ttyAMA1',
                 uart_baudrate=115200,
                 slave_reset_pin=23,
                 remote_host="3.134.62.14",
                 remote_control_port=8485,
                 remote_video_port=8487)
    
    try:
        car.main_loop()
        
    except KeyboardInterrupt:
        GPIO.cleanup()
    
    
    