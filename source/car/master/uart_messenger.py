import RPi.GPIO as GPIO
import serial
import time
import queue
import struct

class UART_Messenger(serial.Serial):
    def __init__(self, device, baud_rate, timeout, reset_pin):
        super().__init__(device, baud_rate, timeout=timeout)
        
        self.reset_pin = reset_pin
        self.reset_input_buffer()
        self.command_queue = queue.Queue()
        
        self.msg_types = ["RPM", "USS", "IMU", "RES", "ERR", "LOG", "DBG"]
        self.text_msg = [0,0,0,0,1,1,1]
        
        self.msg_queues = {i:queue.Queue() for i in range(len(self.msg_types))}
        
 
    def send_reset(self):
        try:
            GPIO.output(self.reset_pin, 1)
            time.sleep(0.1)
            GPIO.output(self.reset_pin, 0)
            return True
        
        except Exception as e:
            print(e)
            return False
        
    def command_worker(self):
        while True:
            # If there are commands in the queue and buffer is free to send
            if not self.command_queue.empty() and self.out_waiting == 0:
                self.send_command(self.command_queue.get())
                
    def message_worker(self):
        while True:
            if self.in_waiting > 3: #Header for each message is 3 bytes
                msg_type, payload = self.fetch_msg()
                self.parse_msg(msg_type, payload)
    
    def send_command(self, command, encoded=False):
        if command == "": return
        
        try:
            if not encoded:
                command += "\n"
                command = command.encode()
            self.write(command)
            return True
        
        except Exception as e:
            print("Could not send message: " + str(e))
            return False
        
    def put_command(self, command):
        self.command_queue.put(command)
        
    def fetch_msg(self):
        msg_header = self.read(3)
        msg_type, payload_length = struct.unpack("<BH", msg_header)
        print(f"type: {msg_type}, length: {payload_length}", end="--- ")
        
        payload = self.read(payload_length)
        return msg_type, payload
                
    def parse_msg(self, msg_type, payload):
        if msg_type == 0x00: # RPM measurement
                rpm = struct.unpack("<f", payload)
                print(f"(RPM)->{rpm}")
            
        elif msg_type == 0x01: # Ultrasonic sensor measurement
            sensor_data = struct.unpack("<Bf", payload)
            side, distance = sensor_data
            print(f"(USS)->{side}: {distance}")
            
        elif msg_type == 0x02: # IMU measurement
            sensor_data = struct.unpack("<6f", payload)
            yaw, pitch, roll, ax, ay, az = sensor_data
            print(f"(IMU)->ypr: {yaw}, {pitch}, {roll} acc: {ax}, {ay}, {az}")
            
        elif msg_type == 0x03: # Command response
            reponse = struct.unpack("<B", payload)
            print(f"(RES)->{response}")
            
        elif msg_type == 0x04: # Error message
            error = payload.decode("utf-8").rstrip()
            print(f"(ERR)->{error}")
            
        elif msg_type == 0x05: # Log message
            log = payload.decode("utf-8").rstrip()
            print(f"(LOG)->{log}")
            
        elif msg_type == 0x06: # Debug message
            debug = payload.decode("utf-8").rstrip()
            print(f"(DEBUG)->{debug}")
            
        else:
            print(f"Unknown message type")
                
                
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
            if self.send_command("OK"):
                return True
        return False