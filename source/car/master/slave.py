import RPi.GPIO as GPIO
from threading import Thread
from multiprocessing import Process
import time
import sys

sys.path.append("/home/jp//Projects/smart-4g-rc-car/source/common")
from socket_relay_client import RelayClientUDP
from mqtt_client import MQTT_Client
from uart_messenger import UARTMessenger
from file_parser import FileParser as fp

class Slave:
    def __init__(self, reset_pin, remote_host, remote_port, mqtt_broker):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(reset_pin, GPIO.OUT)
        
        self.uart = UARTMessenger("/dev/ttyAMA1", 115200)
        self.reset_pin = reset_pin
        self.ready = False
        self.mqtt_ready = False
        
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.mqtt_broker = mqtt_broker
        
        self.param_command_dict = {"STEER_MAX":("Sx","SM"),
                                   "STEER_CENTER":("Sr","Sc"),
                                   "STEER_MIN":("Sn","Sm"),
                                   "PAN_MAX":("Px","PM"),
                                   "PAN_CENTER":("Pr","Pc"),
                                   "PAN_MIN":("Pn","Pm"),
                                   "TILT_MAX":("Tx","TM"),
                                   "TILT_CENTER":("Tr","Tc"),
                                   "TILT_MIN":("Tn","Tm"),
                                   "DRIVE_MAX_POWER":("Dg","Ds")}
        
    def start(self):
        self.main_process = Process(target=self.start_tasks)
        self.main_process.start()
        
    def stop(self):
        self.main_process.terminate()
        self.main_process.join()
        
    def start_tasks(self):
        msg_handling_thread = Thread(target=self.msg_handler, daemon=True)
        msg_handling_thread.start()
        self.setup()
        self.init_mqtt()
        self.publish_current_configuration()
        self.connect_to_remote_control()
        self.start_remote_control()
        
    def setup(self):
        self.ready = False
        self.__connect()
        self.ready = True
        
        print("Setting saved configuration")
        saved_config = fp.parse_conf_file("../saved.conf")
        self.set_configuration(saved_config)
        time.sleep(1)
        
        print("Running startup commands")
        commands = fp.parse_cmd_file("../startup.cmd")
        for command in commands: self.send_command(command)
        time.sleep(1)
        
    def __connect(self):
        print("Attempting UART connection")
        self.send_reset()
        self.uart.wait_for_message("available", timeout=10)
        self.send_command("OK")
        
        while True:
            try:
                self.uart.wait_for_message("ready", timeout=2)    
                self.uart.flushInput()
                time.sleep(0.1)
                break
            except:
                self.send_command("OK")
        
        print("Setup successfull! Slave ready to receive commands...")
        
    def send_command(self, command):
        if command == "": return
        command += "\n"
        command = command.encode()
        self.uart.write(command)
        
    def connect_to_remote_control(self):
        print("Connecting to control relay")
        self.remote_controller = RelayClientUDP(self.remote_host, self.remote_port)
        self.remote_controller.keep_alive()
        
    def start_remote_control(self):
        while True:
            data, address = self.remote_controller.recvfrom(1024)
            if not data: continue
            self.uart.write(data)
            
    def init_mqtt(self):
        self.mqtt_client = MQTT_Client()
        self.mqtt_client.msg_handler = self.mqtt_msg_handler
        self.mqtt_client.connect(self.mqtt_broker)
        self.mqtt_client.loop_start()
        
        self.mqtt_client.subscribe("RCCAR/CMD/SETUP")
        self.mqtt_client.subscribe("RCCAR/CMD/SAVE_CONFIG")
        self.mqtt_ready = True
            
    def msg_handler(self):
        while True:
            if self.ready:
                msg = self.uart.get_msg()
                if not msg: continue
                
                topic, data = msg
                payload = ",".join([str(value) for value in data])
                if self.mqtt_ready: self.mqtt_client.publish(topic=f"RCCAR/DATA/{topic}", payload=payload)
                
    def publish_current_configuration(self):
        print("Publishing current slave configuration")
        current_config = self.get_current_configuration()
        for topic, value in current_config.items():
            if self.mqtt_ready: self.mqtt_client.publish(topic=f"RCCAR/CONFIG/{topic}", payload=str(value), retain=True)
                
    def mqtt_msg_handler(self, topic, msg):
        if topic == "RCCAR/CMD/SETUP":
            self.setup()
            
        elif topic == "RCCAR/CMD/SAVE_CONFIG":
            print("Saving current configuration")
            config = self.get_current_configuration()
            fp.write_conf_file("../saved.conf", config)

    def get_current_configuration(self):
        configuration_values = {}
        for param, (command, _) in self.param_command_dict.items():
            self.send_command(command)
            configuration_values[param] = self.uart.get_response()
        
        print(configuration_values)
        return configuration_values
    
    def set_configuration(self, config):
        for param, value in config.items():
            command = f"{self.param_command_dict[param][1]}{value}"
            self.send_command(command)
        
    def send_reset(self):
        print("Resetting")
        GPIO.output(self.reset_pin, 1)
        time.sleep(0.1)
        GPIO.output(self.reset_pin, 0)
        