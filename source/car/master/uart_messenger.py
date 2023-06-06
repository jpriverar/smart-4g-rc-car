import RPi.GPIO as GPIO
import serial
import time
import struct
import queue

class UARTMessenger(serial.Serial):
    def __init__(self, device, baud_rate):
        super().__init__(device, baud_rate, timeout=1)
        self.reset_input_buffer()
        
        self.is_text_msg = [0,0,0,0,0,1,1,1]
        self.response_queue = queue.Queue()
                
    def get_msg(self):
        if self.in_waiting > 3: #Header for each message is 3 bytes
            try:
                msg_type, payload = self.fetch()
                msg = self.parse(msg_type, payload)
                return msg
            
            except Exception as e:
                print("Error parsing message: " + str(e))
                self.flushInput()
                return None
                    
    def fetch(self):
        msg_header = self.read(3)
        msg_type, payload_length = struct.unpack("<BH", msg_header)
        
        if self.is_text_msg[msg_type]:
            payload = self.readline()
        else:
            payload = self.read(payload_length)
        return msg_type, payload
    
    def parse(self, msg_type, payload):        
        if msg_type == 0x00: # RPM measurement
            rpm = struct.unpack("<f", payload)[0]
            return "RPM", int(rpm)
        
        if msg_type == 0x01: # Speed measurement
            speed = struct.unpack("<f", payload)[0]
            return "SPEED", speed
            
        elif msg_type == 0x02: # Ultrasonic sensor measurement
            side, distance = struct.unpack("<Bf", payload)
            topic = "FUSS" if side else "BUSS"
            return topic, distance
            
        elif msg_type == 0x03: # IMU measurement
            sensor_data = struct.unpack("<6f", payload)
            #print(sensor_data)
            return "IMU", sensor_data
            
        elif msg_type == 0x04: # Command response
            response = struct.unpack("<B", payload)
            self.response_queue.put(response[0])
            
        elif msg_type == 0x05: # Error message
            error = payload.decode("utf-8").strip()
            print(f"(ERROR)->{error}")
            
        elif msg_type == 0x06: # Log message
            log = payload.decode("utf-8").strip()
            print(f"(LOG)->{log}")
            
        elif msg_type == 0x07: # Debug message
            debug = payload.decode("utf-8").strip()
            print(f"(DEBUG)->{debug}")
            
        else:
            print(f"Unknown message type")
            
    def get_response(self, timeout=0.5):
        try: 
            response = self.response_queue.get(block=True, timeout=timeout)
            return response
        except:
            print("Could not fetch any response")
            return None
                
    def wait_for_message(self, msg, timeout):
        start_time = time.time()
        curr_time = time.time()
        
        while (curr_time - start_time) < timeout:
            if self.in_waiting > 0:
                try:
                    # Reading available messages in the input buffer
                    line = self.readline().decode('utf-8').strip()
                    print(line)
                    if msg in line: return
                    
                except Exception as e:
                    print("Bad message: " + str(e))
                    
            curr_time = time.time()
        raise Exception("Timeout reached waiting for message")  
    