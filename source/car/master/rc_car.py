import RPi.GPIO as GPIO
import threading
import time
import sys
import requests

sys.path.append("/home/jp//Projects/smart-4g-rc-car/source/common")
from mqtt_client import MQTT_Client
from video_streamer import VideoStreamer
from sim7600 import SIM7600
from slave import Slave

class RC_Car:
    def __init__(self, remote_host, remote_control_port, remote_video_port, mqtt_broker): 
        self.remote_host = remote_host
        self.remote_video_port = remote_video_port
        self.mqtt_broker = mqtt_broker
            
        self.slave = Slave(reset_pin=23, remote_host=remote_host, remote_port=remote_control_port, mqtt_broker=mqtt_broker)
        
    def start(self):
        print("Starting 4G-RC-CAR")
        self.slave.start()
        time.sleep(5)
        
        self.init_mqtt()
        self.init_gps()
        self.init_video_stream()
        
    def stop(self):
        print("Stopping 4G-RC-CAR")
        self.slave.stop()
        
    def init_mqtt(self):
        self.mqtt_client = MQTT_Client()
        self.mqtt_client.msg_handler = self.mqtt_msg_handler
        self.mqtt_client.will_set(topic="RCCAR/STATUS", payload="OFF", qos=1, retain=True)
        self.mqtt_client.connect(self.mqtt_broker)
        self.mqtt_client.loop_start()
        
        self.mqtt_client.subscribe("RCCAR/CONFIG/COMPRESSION_QUALITY")
        self.mqtt_client.subscribe("RCCAR/CONFIG/IMAGE_RESOLUTION")
        
        self.mqtt_client.publish(topic="RCCAR/STATUS", payload="ON", qos=1, retain=True)
        self.mqtt_ready = True
        
    def init_video_stream(self):
        self.video_streamer = VideoStreamer(self.remote_host, self.remote_video_port)
        self.video_streamer.start()
        
    def init_gps(self):
        self.sim = SIM7600("/dev/ttyS0", 115200, power_key=6)
        gps_update_thread = threading.Thread(target=self.__gps_update_loop, daemon=True)
        gps_update_thread.start()
            
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
                
    def mqtt_msg_handler(self, topic, msg):
        if topic == "RCCAR/CONFIG/COMPRESSION_QUALITY":
            print("compression quality changed")
        
        elif topic == "RCCAR/CONFIG/IMAGE_RESOLUTION":
            print("image resolution changed")
        
        else:
            print(f'{topic} message recieved: {m_decode}')
            

def is_connection_active(timeout=1):
    try:
        requests.head("http://www.google.com/", timeout=timeout)
        return True
    except requests.ConnectionError:
        return False
    
def wait_for_network_connection():
    print("Waiting for internet connection...")
    honk_state = 0
    while True:
        if is_connection_active():
            car.slave.send_command("H0")
            honk_burst()
            print("Connection is active!")
            return
            
        else:
            honk_state ^= 1
            car.slave.send_command(f"H{honk_state}")
            time.sleep(1.5)
            
def honk_burst():
    for i in range(3):
        car.slave.send_command("H1")
        time.sleep(0.2)
        car.slave.send_command("H0")
        time.sleep(0.2)
        
    
if __name__ == "__main__":
    REMOTE_HOST = "3.134.62.14"
    REMOTE_CONTROL_PORT = 8485
    REMOTE_VIDEO_PORT = 8487
    
    car = RC_Car(REMOTE_HOST, REMOTE_CONTROL_PORT, REMOTE_VIDEO_PORT, REMOTE_HOST)
    wait_for_network_connection()    
    
    car.start()
        
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        car.stop()
        GPIO.cleanup()
    
    
    
