import RPi.GPIO as GPIO
import time
import serial
import threading
from utils import transform_gps_coordinates

class SIM7600(serial.Serial):
    def __init__(self, serial_dev_path, baud_rate, power_key):
        super().__init__(serial_dev_path, baud_rate)
        self.on = True
        self.power_key = power_key
        GPIO.setup(power_key, GPIO.OUT)
        
        self.recv_buffer = ""
        
    def press_power_button(self):
        GPIO.output(self.power_key,GPIO.HIGH)
        time.sleep(1)
        GPIO.output(self.power_key,GPIO.LOW)
        
    def power_on(self):
        # If already on, return
        if self.on: return
        print('SIM7600X is starting:')
        self.press_power_button()
        time.sleep(15)
        self.flushInput()
        self.on = True
        print('SIM7600X is ready')
        
    def power_off(self):
        # If already off, return
        if not self.on: return
        print("SIM7600 is logging of...")
        self.press_power_button()
        time.sleep(15)
        self.on = False
        print("Good bye!")
        
    def send_at(self, command, expected="OK", timeout=0.05):
        self.recv_buffer = ""
        # Writing the command to the serial port
        self.write((command + "\r\n").encode())
        print(command) # To verify it's has been sent
        time.sleep(0.05)
        self.fetch_response(expected, timeout)
        
    def fetch_response(self, expected, timeout):
        start = time.time()
        curr = time.time()
        while curr - start < timeout:
            if self.in_waiting > 0:
                msg = self.readline().decode("utf-8").strip() # Get the most recent line recieved
                if expected in msg: return True
                elif "ERROR" in msg: return False
                
                if msg != "": self.recv_buffer = msg
                
            curr = time.time() # Updating the curr time value
        return False
            
    def network_config(self, APN=None):
        if APN is not None:
            self.send_at('AT+CGDCONT=1,"IP","{APN}"', timeout=3)
        self.send_at("AT+CSQ", timeout=0.25)
        self.send_at("AT+CREG?", timeout=0.25)
        self.send_at('AT+CIPMODE=1', timeout=0.25)
        self.send_at('AT+CSOCKSETPN=1', timeout=0.25)
        self.send_at('AT+CIPMODE=0', timeout=0.25)
        
    def network_up(self):
        self.send_at('AT+NETOPEN', expected="+NETOPEN: 0", timeout=10)
        
    def network_down(self):
        self.send_at('AT+NETCLOSE', expected="+NETCLOSE: 0", timeout=3)
        
    def gps_up(self):
        self.send_at('AT+CGPS=1,1', expected="OK", timeout=1)
        
    def gps_down(self):
        self.send_at('AT+CGPS=0', expected="+CGPS: 0", timeout=1)
        
    def get_gps_coordinates(self):
        self.send_at('AT+CGPSINFO', expected="OK", timeout=1)
        raw_coordinates = self.recv_buffer[11:]
        return transform_gps_coordinates(raw_coordinates)
        
        

if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    sim = SIM7600("/dev/ttyS0", 115200, power_key=6)
    #sim.power_on()

    #sim.network_config()
    #sim.network_up()
    #time.sleep(3)
    #sim.network_down()
    
    #sim.power_off()
    
    while True:
        print("New coords")
        lat, lon = sim.get_gps_coordinates()
        print(lat, lon)
        time.sleep(2)

            
            
