import RPi.GPIO as GPIO
import serial
import time
import struct

class UART_Messenger(serial.Serial):
    def __init__(self, device, baud_rate, timeout, reset_pin, mqtt_client=None):
        super().__init__(device, baud_rate, timeout=timeout)
        
        self.reset_pin = reset_pin
        self.reset_input_buffer()
        
        self.msg_types = ["RPM", "USS", "IMU", "RES", "ERR", "LOG", "DBG"]
        self.is_text_msg = [0,0,0,0,1,1,1]
        
        self.mqtt = False
        if mqtt_client is not None:
            self.mqtt = True
            self.mqtt_client = mqtt_client
 
    def send_reset(self):
        GPIO.output(self.reset_pin, 1)
        time.sleep(0.1)
        GPIO.output(self.reset_pin, 0)
                
    def message_worker(self):
        while True:
            if self.in_waiting > 3: #Header for each message is 3 bytes
                msg_type, payload = self.fetch_msg()
                try:
                    self.parse_msg(msg_type, payload)
                except Exception:
                    print("Error parsing message")
                    self.flushInput()
                    
    
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
        
        
    def fetch_msg(self):
        msg_header = self.read(3)
        msg_type, payload_length = struct.unpack("<BH", msg_header)
        print(f"type: {msg_type}, length: {payload_length}")
        
        if self.is_text_msg[msg_type]:
            payload = self.readline()
        else:
            payload = self.read(payload_length)
        return msg_type, payload
                
    def parse_msg(self, msg_type, payload):
        if msg_type == 0x00: # RPM measurement
            gear, rpm = struct.unpack("<Bf", payload)
            if self.mqtt:
                self.mqtt_client.publish(topic=f"RCCAR-RPM", payload=f"{gear},{int(rpm)}")
            
        elif msg_type == 0x01: # Ultrasonic sensor measurement
            sensor_data = struct.unpack("<Bf", payload)
            side, distance = sensor_data
            topic_suffix = "FUSS" if side else "BUSS"
            if self.mqtt:
                self.mqtt_client.publish(topic=f"RCCAR-{topic_suffix}", payload=distance)
            
        elif msg_type == 0x02: # IMU measurement
            sensor_data = struct.unpack("<6f", payload)
            yaw, pitch, roll, ax, ay, az = sensor_data
            print(f"(IMU)->ypr: {yaw}, {pitch}, {roll} acc: {ax}, {ay}, {az}")
            
        elif msg_type == 0x03: # Command response
            reponse = struct.unpack("<B", payload)
            print(f"(RES)->{response}")
            
        elif msg_type == 0x04: # Error message
            error = payload.decode("utf-8").strip()
            print(f"(ERR)->{error}")
            
        elif msg_type == 0x05: # Log message
            log = payload.decode("utf-8").strip()
            print(f"(LOG)->{log}")
            
        elif msg_type == 0x06: # Debug message
            debug = payload.decode("utf-8").strip()
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
                    line = self.readline().decode('utf-8').strip()
                    print(line)
                    if line == msg: return
                    
                except Exception as e:
                    print("Bad message: " + str(e))
                    
            curr_time = time.time()
        raise Exception("Timeout reached waiting for message")
        
    def wait_for_connection(self, timeout=10):
        self.wait_for_message("available", timeout=timeout)
        self.send_command("OK")    
    