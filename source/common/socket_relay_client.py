import socket
import select
import threading
import time
from thread_safe_socket import ThreadSafeSocket

class RelayClientTCP:
    def __init__(self):
        self.connected = False

    def connect(self, host, port):
        self._socket = ThreadSafeSocket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((host, port))
        print("Client connected, waiting for relay to open...")

        # Wait for message to start sending data
        while not self.connected:
            msg = self._socket.recv(1024).decode('utf-8')
            if msg == "OK": 
                print("Socket relay active...")
                print("Ready to start communication")
                self.connected = True

    def send(self, data):
        if self.connected:
            try:
                self._socket.send(data)
            
            except Exception as e:
                print("Something went wrong: " + str(e))
                self._socket.close()
                self.connected = False

    def sendall(self, data):
        if self.connected:
            try:
                self._socket.sendall(data)

            except Exception as e:
                print("Something went wrong: " + str(e))
                self._socket.close()
                self.connected = False
    
    def recv(self, buffer_size):
        if self.connected:
            try:
                data = None
                ready_to_read, _, _ = select.select([self._socket], [], [], 0)
                
                if ready_to_read:
                    data = self._socket.recv(buffer_size)
                    if not data:
                        raise Exception
                return data

            except Exception as e:
                print("Something went wrong: " + str(e))
                self._socket.close()
                self.connected = False

class RelayClientUDP:
    def __init__(self, host, port):
        self._socket = ThreadSafeSocket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = host
        self.port = port

    def recvfrom(self, buffer_size):
        ready_to_read, _, _ = select.select([self._socket], [], [], 0)
        if ready_to_read:
            data, address = self._socket.recvfrom(buffer_size)
            return data, address
        else:
            return None, None
        
    def sendto(self, data, address=None):
        if not address: 
            address = (self.host, self.port)
        else:
            self.host, self.port = address
        self._socket.sendto(data, address)
        
    def heartbeat(self):
        self.sendto("OK".encode())
        
    def __keep_alive_loop(self, period=5):
        while True:
            self.heartbeat()
            time.sleep(period)
            
    def keep_alive(self):
        keep_alive_thread = threading.Thread(target=self.__keep_alive_loop, daemon=True)
        keep_alive_thread.start()
            
            
            