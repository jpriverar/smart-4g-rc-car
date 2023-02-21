import RPi.GPIO as GPIO
import serial
import time
from collections import deque
import struct

class UART_Messenger(serial.Serial):
    def __init__(self, device, baud_rate, timeout, reset_pin):
        super().__init__(device, baud_rate, timeout=timeout)
        
        self.reset_pin = reset_pin
        self.reset_input_buffer()
        self.msg_queue = deque([])
 
    def send_reset(self):
        try:
            GPIO.output(self.reset_pin, 1)
            time.sleep(0.1)
            GPIO.output(self.reset_pin, 0)
            return True
        
        except Exception as e:
            print(e)
            return False
    
    def send_msg(self, msg):
        try:
            msg = msg + "\n"
            msg = msg.encode()
            self.write(msg)
            return True
        
        except Exception as e:
            print(e)
            return False
        
    def fetch_msg(self):
        #try:
        if self.in_waiting > 0: #Header for each message is 3 bytes
            msg_header = self.read(3)
            msg_type, payload_length = struct.unpack("<BH", msg_header)
            print(hex(msg_type), hex(payload_length))
            
            if msg_type == 0x01: # Ultrasonic sensor measurement
                sensor_data = struct.unpack("<Bf", self.read(payload_length))
                side, distance = sensor_data
                print(f"{side}: {distance}")
                
            elif msg_type == 0x02: # IMU measurement
                sensor_data = struct.unpack("<6f", self.read(payload_length))
                yaw, pitch, roll, ax, ay, az = sensor_data
                print(f"ypr: {yaw}, {pitch}, {roll} acc: {ax}, {ay}, {az}")
                    
                #line = self.readline().decode('utf-8').rstrip()
                #self.msg_queue.append(line)
                
        #except Exception as e:
            #print("Could not fetch message: " + str(e))
                
    def wait_for_message(self, msg, timeout):
        start_time = time.time()
        curr_time = time.time()
        
        while (curr_time - start_time) < timeout:
            if self.in_waiting > 0:
                try:
                    # Reading available messages in the input buffer
                    line = self.readline().decode('utf-8').rstrip()
                    print(line)
                    if line == msg:
                        return True
                    
                except Exception as e:
                    print("Bad message: " + str(e))
                    
            curr_time = time.time()
        return False
        
    def wait_for_connection(self, timeout=10):
        if self.wait_for_message("available", timeout=timeout):
            if self.send_msg("OK"):
                return True
        return False
            


if __name__ == "__main__":
    # GPIO setup
    GPIO.setmode(GPIO.BCM)
    reset_pin = 23
    GPIO.setup(reset_pin, GPIO.OUT)

    # Creating arduino comms instance
    slave = UART_Messenger('/dev/ttyAMA1', 115200, timeout=1, reset_pin=reset_pin)

    # Sending a reset_signal to the arduino
    print("Resetting slave")
    ret = slave.send_reset()
    if not ret:
        print("Something went wrong, exitting...")
        exit()

    # Waiting till connection is stablished
    print("Attempting UART connection with slave")
    ret = slave.wait_for_connection(timeout=5)
    if not ret:
        print("Timeout reached, could not stablish connection with slave!")
        exit()
        
    print("Setup successfull! Slave ready to receive commands...")