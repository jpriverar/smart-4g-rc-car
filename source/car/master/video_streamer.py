from picamera2 import Picamera2
from picamera2.encoders import H264Encoder, JpegEncoder
from picamera2.outputs import FileOutput
import sys
import cv2
import math
import threading
import zlib
import time
import socket

sys.path.append("/home/jp/Projects/smart-4g-rc-car/source/common")
from socket_relay_client import RelayClientUDP

class VideoStreamer:
    def __init__(self, remote_host, remote_port):
        # Initializing the camera
        self.cam = Picamera2()
        config = self.cam.create_video_configuration(main={"size":(640, 480), "format":"RGB888"}, lores={"size":(320, 240), "format": "YUV420"}, controls={"FrameRate":30})
        self.cam.configure(config)
        self.encoder = JpegEncoder(q=30)
        
        self.compression_quality = 50
        self.scale_percent = 100
        
        # Client for socket relay
        print("Connecting to video relay")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect((remote_host, remote_port))
        self.stream = sock.makefile("wb")
        
    def start(self):
        self.cam.start_recording(self.encoder, FileOutput(self.stream))