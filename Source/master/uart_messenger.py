import RPi.GPIO as GPIO
import serial
import time
from collections import deque

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
            print("Reset sent...")
            return 0
        except Exception as e:
            print("Could not send reset signal: " + str(e))
            return 1
    
    def send_msg(self, msg):
        try:
            msg = msg + "\n"
            msg = msg.encode()
            self.write(msg)
            return 0
        except:
            print("Could not send msg, please check it is UTF-8 encodable")
            return 1
        
    def fetch_msg(self):
        try:
            if self.in_waiting > 0:
                line = self.readline().decode('utf-8').rstrip()
                self.msg_queue.append(line)
                print(line)
        except Exception as e:
            print("Could not fetch message: " + str(e))
        
    def wait_for_connection(self, timeout=3):
        print("Attempting connection with arduino")
        start_time = time.time()
        curr_time = time.time()
        
        while (curr_time - start_time) < timeout:
            # If a message is available in the buffer
            if self.in_waiting > 0:
                try:
                    line = self.readline().decode('utf-8').rstrip()
                    if line == "ready":
                        self.send_msg("OK")
                        print("Connection successful!")
                    return 0
                except:
                    print("Received bad formatted message, skipping...")
                    
            curr_time = time.time()
        print("Connection timeout...")
        return 1
