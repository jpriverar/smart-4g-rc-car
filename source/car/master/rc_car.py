import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
from utils import *
import threading
from multiprocessing import Process
import time
import sys

sys.path.insert(1, "/home/jp/Projects/smart-4g-rc-car/source/common")
from socket_relay_client import RelayClientUDP
from uart_messenger import UART_Messenger
from video_streamer import VideoStreamer
from sim7600 import SIM7600

class RC_Car:
    def __init__(self, uart_path, uart_baudrate, slave_reset_pin, remote_host, remote_control_port, remote_video_port):
        # GPIO setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(slave_reset_pin, GPIO.OUT)
        
        # Creating arduino comms instance
        self.slave = UART_Messenger(uart_path, uart_baudrate, timeout=1, reset_pin=slave_reset_pin)
        self.car_setup()
        
        # Applying initial configuration file
        print("Applying saved vonfiguration")
        self.apply_configuration_file("../saved.conf")
        
        print("Running startup commands")
        self.apply_command_file("../startup.cmd")
    
        self.remote_host = remote_host
        self.remote_control_port = remote_control_port
        self.remote_video_port = remote_video_port        
        
    def car_setup(self):
        print("Resetting slave")
        self.slave.send_reset()

        print("Attempting UART connection with slave")
        self.slave.wait_for_connection(timeout=5)
            
        print("Waiting for all components to be initialized by slave...")
        self.slave.wait_for_message("ready", timeout=10)
            
        self.slave.flushInput()
        print("Setup successfull! Slave ready to receive commands...")
        
    def init_MQTT(self):
        id = generate_mqtt_client_id()
        self.mqtt_client = mqtt.Client(id)
        self.mqtt_client.on_connect = self.__on_mqtt_connect
        self.mqtt_client.on_disconnect = self.__on_mqtt_disconnect
        self.mqtt_client.on_message = self.__on_mqtt_message
        
        self.mqtt_client.will_set(topic="RCCAR/STATUS", payload="OFF", qos=1, retain=True)
        self.mqtt_client.connect(self.remote_host)
        self.mqtt_client.loop_start()
        self.mqtt_client.publish(topic="RCCAR/STATUS", payload="ON", qos=1, retain=True)
        
        msg_publisher_thread = threading.Thread(target=self.publish_car_messages_loop, daemon=True)
        msg_publisher_thread.start()
        
    def init_GPS(self):
        self.sim = SIM7600("/dev/ttyS0", 115200, power_key=6)
        self.gps_continuous_update()
        
    def init_remote_control(self):
        print("Connecting to control relay")
        self.remote_controller = RelayClientUDP(self.remote_host, self.remote_control_port)
        self.remote_controller.keep_alive()
        self.remote_control_loop()
        
    def init_video_stream(self):
        self.video_streamer = VideoStreamer(self.remote_host, self.remote_video_port)
        self.video_streamer.start()
        
    def apply_command_file(self, command_file_path):
        commands = get_command_file_commands(command_file_path)
        for command in commands:
            self.slave.send_command(command)
            
    def apply_configuration_file(self, config_file_path):
        commands = get_config_file_commands(config_file_path)
        for command in commands:
            self.slave.send_command(command)
            
    def publish_current_configuration(self):
        current_config = get_current_configuration(self.slave)
        for topic, value in current_config.items():
            self.mqtt_client.publish(topic=f"RCCAR/CONFIG/{topic}", payload=str(value), retain=True)
            
    def __gps_update_loop(self):
        while True:
            try:
                lat, lon = self.sim.get_gps_coordinates()
                self.mqtt_client.publish(topic="RCCAR/DATA/POS", payload=f'{{ "name":"rc-car", "lat":{lat}, "lon":{lon}, "icon":"arrow", "radius":50 }}', qos=1, retain=True)
                time_to_sleep = 3
            except:
                time_to_sleep = 15
            finally:
                time.sleep(time_to_sleep)
    
    def gps_continuous_update(self):
        gps_update_thread = threading.Thread(target=self.__gps_update_loop, daemon=True)
        gps_update_thread.start()
    
    def remote_control_loop(self):
        while True:
            data, address = self.remote_controller.recvfrom(1024)
            if not data: continue
            self.slave.send_command(data, encoded=True)
            
    def publish_car_messages_loop(self):
        while True:
            msg = self.slave.get_msg()
            if not msg: continue
            topic, payload = msg
            self.mqtt_client.publish(topic=f"RCCAR/DATA/{topic}", payload=str(payload))
            
    def __on_mqtt_connect(self, client, userdata, flags, rc):
        if rc: print(f"A problem occured, could not connect to the broker: {self.remote_host}")
        else: print(f"Succesfully connected to broker: {self.remote_host}")
            
    def __on_mqtt_disconnect(self, client, userdata, flags, rc=0):
        if rc: print(f"A problem occured, could not disconnect from the broker: {self.remote_host}")
        else: print(f"Succesfully disconnected from broker: {self.remote_host}")
            
    def __on_mqtt_message(self, client, userdata, msg):
        topic = msg.topic
        m_decode = str(msg.payload.decode("utf-8", "ignore"))
        print(f'{topic} message recieved: {m_decode}')
    
if __name__ == "__main__":
    car = RC_Car(uart_path='/dev/ttyAMA1',
                 uart_baudrate=115200,
                 slave_reset_pin=23,
                 remote_host="3.134.62.14",
                 remote_control_port=8485,
                 remote_video_port=8487)
    
    car.init_MQTT()
    car.publish_current_configuration()
    car.init_GPS()
    car.init_video_stream()
    car.init_remote_control()
        
    try:
        pass
    except Exception as e:
        print(str(e))
        GPIO.cleanup()
    
    
    