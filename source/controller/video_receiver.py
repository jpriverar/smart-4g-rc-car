import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QThread, pyqtSignal
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi
import cv2
import numpy as np
import time
import zlib

sys.path.append("../common")
from socket_relay_client import RelayClientUDP, RelayClientTCP

class UDPVideoThread(QThread):
    change_pixmap = pyqtSignal(QImage)
    
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.fps = 0
        self.frame_counter = 0
        self.packet_size = 0
    
    def run(self):
        video_client = RelayClientUDP(self.host, self.port)
        video_client.keep_alive()

        max_datagram_size = 65536
        frame_time = time.time()
        while True:
            
            buffer, address = video_client.recvfrom(max_datagram_size)
            if not buffer: continue

            # Decoding the image
            self.packet_size = len(buffer)
            self.frame_counter += 1
            frame = cv2.imdecode(np.frombuffer(buffer, dtype=np.uint8), cv2.IMREAD_COLOR)
            #frame = cv2.cvtColor(frame, cv2.COLOR_YUV420P2RGB)

            try: 
                # Convert the image to QImage and emit the signal
                height, width, channel = frame.shape
                bytesPerLine = channel * width
                qImg = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
                self.change_pixmap.emit(qImg)

                # Updating fps
                if self.frame_counter%20 == 0:
                    self.fps = self.frame_counter/(time.time() - frame_time)
                    frame_time = time.time()
                    self.frame_counter = 0

            except Exception as e:
                print(str(e))

class TCPVideoThread(QThread):
    change_pixmap = pyqtSignal(QImage)

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.fps = 0

    def run(self):
        video_client = RelayClientTCP()
        video_client.connect(self.host, self.port)
        
        while True:
            # Getting the size of the image
            size_data = video_client.recv(4)
            size = int.from_bytes(size_data, byteorder="big")

            # Waiting to get the whole image
            data = b""
            while len(data) < size:
                data += video_client.recv(size - len(data))

            # Decoding the image
            frame = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)

            # Convert the image to QImage and emit the signal
            height, width, channel = frame.shape
            bytesPerLine = 3 * width
            qImg = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
            self.change_pixmap.emit(qImg)