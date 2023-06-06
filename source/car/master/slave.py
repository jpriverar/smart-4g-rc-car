import RPi.GPIO as GPIO
from threading import Thread
import time
import sys

sys.path.append("/home/jp//Projects/smart-4g-rc-car/source/common")
from mqtt_client import MQTT_Client
from uart_messenger import UARTMessenger
from file_parser import FileParser as fp

class Slave:
    def __init__(self, reset_pin):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(reset_pin, GPIO.OUT)
        
        self.uart = UARTMessenger("/dev/ttyAMA1", 115200)
        self.reset_pin = reset_pin
        self.ready = False
        
        self.data = {"RPM": 0,
                     "SPEED": 0,
                     "FUSS": 0,
                     "BUSS": 0,
                     "IMU": (0,0,0,0,0,0)}
        
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
        msg_handling_thread = Thread(target=self.msg_handler, daemon=True)
        msg_handling_thread.start()
        self.setup()
                
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
        
        print("Setup sucessful")
        
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
        
    def write(self, data):
        self.uart.write(data)
            
    def msg_handler(self):
        while True:
            if self.ready:
                msg = self.uart.get_msg()
                if not msg: continue
                
                topic, data = msg
                self.data[topic] = data

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
            
    def save_current_configuration(self):
        config = self.get_current_configuration()
        fp.write_conf_file("../saved.conf", config)
        
    def send_reset(self):
        print("Resetting")
        GPIO.output(self.reset_pin, 1)
        time.sleep(0.1)
        GPIO.output(self.reset_pin, 0)
        
    def print_data(self):
        max_length = max(len(str(value)) for value in self.data.values())
        
        for value in self.data.values():
            print(f"{str(value):<{max_length}}", end=" ")
        print()
        
if __name__ == "__main__":
    slave = Slave(reset_pin=23)
    slave.attach_remote_control("3.134.62.14", 8485)
    slave.start()
    
    while True:
        time.sleep(1000)