#!/usr/bin/python

import RPi.GPIO as GPIO
import serial
import time
from sim7600 import SIM7600

class socket_AT:
    def __init__(self, sim_module, link, socket_protocol):
        self.link = link
        self.sim = sim_module
        self.protocol = socket_protocol
        
    def connect(self, host, port):
        self.sim.send_at(f'AT+CIPOPEN={self.link},"{self.protocol}","{host}",{port}', expected="+CIPOPEN: 0,0", timeout=10)
    
    def close(self):
        self.sim.send_at(f'AT+CIPCLOSE={self.link}', expected="+CIPCLOSE: 0,0", timeout=10)
    
    def send(self, data):
        size = len(data)
        self.sim.send_at(f'AT+CIPSEND={self.link},{size}', expected=">", timeout=15, new_line=False)
        self.sim.write(data)
        self.sim.fetch_response("+CIPSEND: {self.link},{size},{size}", 2)
    
    def recv(self, bytes):
        bytes = min(bytes, 1500)
        self.sim.send_at(f'AT+CIPRXGET=2,{self.link},{bytes}', timeout=5)
        
    
if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    sim = SIM7600("/dev/ttyS0", 115200, power_key=6)
    sim.power_on()

    sim.network_config()
    sim.network_up()
    time.sleep(3)
    
    client_socket = socket_AT(sim, 0, "TCP")
    client_socket.connect("3.134.62.14", 8485)
    
    msg = "hola hola"
    client_socket.send(msg.encode())
    
    client_socket.recv(1024)
    
    client_socket.close()
    sim.network_down()
    
    sim.power_off()
    