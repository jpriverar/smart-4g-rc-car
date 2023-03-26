import RPi.GPIO as GPIO
import time
import serial
import threading

class SIM7600(serial.Serial):
    def __init__(self, serial_dev_path, baud_rate, power_key):
        super().__init__(serial_dev_path, baud_rate)
        self.on = False
        self.power_key = power_key
        GPIO.setup(power_key, GPIO.OUT)
        
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
        
    def send_at(self, command, expected="OK", timeout=0.05, new_line=True):
        # Writing the command to the serial port
        self.write((command + "\r\n").encode())
        print(command) # To verify it's has been sent
        time.sleep(0.05)
        self.fetch_response(expected, timeout, new_line)
        
    def fetch_response(self, expected, timeout, new_line=True):
        start = time.time()
        curr = time.time()
        while curr - start < timeout:
            if self.in_waiting > 0:
                if new_line:
                    msg = self.readline()
                else:
                    msg = self.read(self.in_waiting)
                msg = msg.decode("utf-8").rstrip() # Get the most recent line recieved
                print(msg)
                
                if expected in msg: return True
                elif "ERROR" in msg: return False
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
        self.send_at('AT+NETOPEN', expected="+NETOPEN: 0" ,timeout=10)
        
    def network_down(self):
        self.send_at('AT+NETCLOSE', expected="+NETCLOSE: 0", timeout=3)

if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    sim = SIM7600("/dev/ttyS0", 115200, power_key=6)
    sim.power_on()

    sim.network_config()
    sim.network_up()
    time.sleep(3)
    sim.network_down()
    
    sim.power_off()
