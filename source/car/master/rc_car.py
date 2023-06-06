import RPi.GPIO as GPIO
import time
import sys
from threading import Thread
from multiprocessing import Process, Value
from slave import Slave
from camera import Camera
from sim7600 import SIM7600
from image_processor import ImageProcessor
from lane_detector import LaneDetector

sys.path.append("/home/jp/Projects/smart-4g-rc-car/source/common")
from socket_relay_client import RelayClientUDP
from mqtt_client import MQTT_Client

class RC_Car:
    def __init__(self):
        self.params = {"mqtt": False,
                       "remote_control": False,
                       "streaming": False,
                       "gps": False,
                       "mode": "manual"}
        
        self.cam = Camera()
        self.lane_detector = LaneDetector(n_windows=15, window_width=50)
        self.slave = Slave(reset_pin=23)
        self.slave.start()
                    
    def start(self):
        print("Starting 4G-RC-CAR")
        
        if self.params["mqtt"]:
            print("Starting MQTT client")
            self.mqtt_client.loop_start()
            self.mqtt_client.publish(topic="RCCAR/STATUS", payload="ON", qos=1, retain=True)
            mqtt_publisher_thread = Thread(target=self.car_data_publisher, daemon=True)
            mqtt_publisher_thread.start()
        
        if self.params["remote_control"]:
            print("Starting remote control")
            remote_controller_thread = Thread(target=self.remote_control_handler, daemon=True)
            remote_controller_thread.start()
        
        if self.params["gps"]:
            print("Starting GPS")
            gps_update_thread = Thread(target=self.gps_update_loop, daemon=True)
            gps_update_thread.start()
            
        camera_feed_thread = Thread(target=self.camera_loop, daemon=True)
        camera_feed_thread.start()
        
    def stop(self):
        print("Stopping 4G-RC-CAR")
        
    def attach_remote_control(self, remote_host, remote_port):
        self.remote_controller = RelayClientUDP(remote_host, remote_port)
        self.params["remote_control"] = True
        self.remote_controller.keep_alive()
        
    def remote_control_handler(self):
        while self.params["remote_control"] and self.params["mode"] == "manual":
            data, address = self.remote_controller.recvfrom(1024)
            if not data: continue
            self.slave.write(data)
        
    def attach_mqtt_client(self, broker):
        self.mqtt_client = MQTT_Client()
        self.mqtt_client.msg_handler = self.mqtt_msg_handler
        self.mqtt_client.will_set(topic="RCCAR/STATUS", payload="OFF", qos=1, retain=True)
        self.mqtt_client.connect(broker)
        
        self.mqtt_client.subscribe("RCCAR/CONFIG/COMPRESSION_QUALITY")
        self.mqtt_client.subscribe("RCCAR/CONFIG/IMAGE_RESOLUTION")
        self.mqtt_client.subscribe("RCCAR/CMD/SETUP")
        self.mqtt_client.subscribe("RCCAR/CMD/SAVE_CONFIG")
        self.mqtt_client.subscribe("RCCAR/CMD/MODE")
        self.params["mqtt"] = True
        
    def mqtt_msg_handler(self, topic, msg):
        if topic == "RCCAR/CONFIG/COMPRESSION_QUALITY":
            print("compression quality changed")
        
        elif topic == "RCCAR/CONFIG/IMAGE_RESOLUTION":
            print("image resolution changed")
            
        elif topic == "RCCAR/CMD/SETUP":
            self.slave.setup()

        elif topic == "RCCAR/CMD/SAVE_CONFIG":
            self.slave.save_current_configuration()
            
        elif topic == "RCCAR/CMD/MODE":
            mode = msg.lower()
            self.params["mode"] = mode
            
            if mode == "manual":
                print("Starting remote control")
                remote_controller_thread = Thread(target=self.remote_control_handler, daemon=True)
                remote_controller_thread.start()
        else:
            print(f'{topic} message recieved: {m_decode}')
            
    def car_data_publisher(self):
        msg_period = 0.3
        while True:
            self.mqtt_client.publish(topic="RCCAR/DATA/RPM", payload=str(self.slave.data["RPM"]))
            #self.mqtt_client.publish(topic="RCCAR/DATA/ACC", payload=pass)
            self.mqtt_client.publish(topic="RCCAR/DATA/SPEED", payload=str(self.slave.data["SPEED"]))
            time.sleep(msg_period)            
        
    def attach_streamer(self, remote_host, remote_port):
        self.streamer = RelayClientUDP(remote_host, remote_port)
        self.params["streaming"] = True
        
    def camera_loop(self):
        self.cam.start()
        
        while True:
            frame = self.cam.capture_array("main")
            
            if self.params["mode"] == "auto":
                pos_error, angle_error = self.get_lane_error(frame)

            if self.params["streaming"]:
                encoded_frame = ImageProcessor.encode_frame(frame, 50)
                self.streamer.sendto(encoded_frame)
                
    def get_lane_error(self, frame):
        undistorted_frame = ImageProcessor.undistort_frame(frame)
        roi = ImageProcessor.extract_roi(undistorted_frame, 0.4)
        
        warped_roi = ImageProcessor.get_bird_eye_view(roi)
        warped_mask = ImageProcessor.preprocess_frame(roi)
        
        self.lane_detector.find_lanes(warped_mask, warped_roi)
        self.lane_detector.find_lanes_center(warped_roi)
        
        unwarped_roi = ImageProcessor.undo_bird_eye_view(warped_roi)
        undistorted_frame[undistorted_frame.shape[0]-unwarped_roi.shape[0]:, :, :] = unwarped_roi
        frame = undistorted_frame
        
        return self.lane_detector.get_lane_data(frame)
                
    def attach_gps(self):
        self.sim = SIM7600("/dev/ttyS0", 115200, power_key=6)
        self.params["gps"] = True
            
    def gps_update_loop(self):
        self.sim.gps_up()
        while True and self.params["gps"]:
            try:
                lat, lon = self.sim.get_gps_coordinates()
                self.mqtt_client.publish(topic="RCCAR/DATA/POS", payload=f'{{ "name":"rc-car", "lat":{lat}, "lon":{lon}, "icon":"arrow", "radius":50 }}', qos=1, retain=True)
                time.sleep(5)
            except Exception as e:
                print(str(e))
                time.sleep(15)
            
    def publish_current_configuration(self):
        print("Publishing current slave configuration")
        current_config = self.slave.get_current_configuration()
        for topic, value in current_config.items():
            self.mqtt_client.publish(topic=f"RCCAR/CONFIG/{topic}", payload=str(value), retain=True)
        