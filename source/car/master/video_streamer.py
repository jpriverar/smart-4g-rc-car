from picamera2 import Picamera2
import sys
import cv2
import math

sys.path.insert(1, "/home/jp/Projects/smart-4g-rc-car/source/common")
from socket_relay_client import RelayClientUDP

class Video_Streamer:
    def __init__(self, remote_host, remote_port):
        # Initializing the camera
        self.cam = Picamera2()
        config = self.cam.create_preview_configuration(main={"size": (640, 480), "format":"RGB888"})
        self.cam.configure(config)
        
        # Client for socket relay
        print("Connecting to video relay")
        self.remote_controller = RelayClientUDP(remote_host, remote_port)
        self.remote_controller.sendto("OK".encode())
        self.relay_host = remote_host
        self.relay_port = remote_port
        
    def start(self):
        self.cam.start()
        while True:
            buffer = self.get_encoded_frame()
            self.send_encoded_frame(buffer)
        
    def get_encoded_frame(self):
        frame = self.cam.capture_array("main")
        result, encoded_frame = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY),30])
        buffer = encoded_frame.tobytes()
        return buffer
        
    def send_encoded_frame(self, buffer):
        # Sending the serialized frame through the socket in chunks
        size = len(buffer)
        max_datagram_size = 65536
        
        #packets = math.ceil(size / max_datagram_size)
        #self.remote_controller.sendto(packets.to_bytes(4, byteorder="big"))
        
        #for i in range(packets):
            #data = buffer[i*(max_datagram_size):(i+1)*(max_datagram_size)]
        self.remote_controller.sendto(buffer)

