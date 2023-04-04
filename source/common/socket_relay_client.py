import socket
import select
from thread_safe_socket import ThreadSafeSocket

class SocketRelayClient:
    def __init__(self, type="TCP"):
        self.connected = False
        self.type = type

        if type == "UDP":
            self._socket = ThreadSafeSocket(socket.AF_INET, socket.SOCK_DGRAM)

    def connect(self, host, port):
        if self.type == "UPD": raise Exception("Cannot 'connect' to UDP sockets...")

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
        if self.type == "UPD": raise Exception("Cannot 'send' to UDP sockets...")
        if self.connected:
            try:
                self._socket.send(data)
            
            except Exception as e:
                print("Something went wrong: " + str(e))
                self._socket.close()
                self.connected = False

    def sendall(self, data):
        if self.type == "UPD": raise Exception("Cannot 'send' to UDP sockets...")
        if self.connected:
            try:
                self._socket.sendall(data)

            except Exception as e:
                print("Something went wrong: " + str(e))
                self._socket.close()
                self.connected = False
    
    def recv(self, buffer_size):
        if self.type == "UPD": raise Exception("Cannot 'receive' from UDP sockets...")
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

    def recvfrom(self, buffer_size):
        if self.type == "TCP": raise Exception("Cannot 'receive from' with TCP sockets...")
        ready_to_read, _, _ = select.select([self._socket], [], [], 0)
        if ready_to_read:
            data, address = self._socket.recvfrom(buffer_size)
            return data, address
        else:
            return None, None
        
    def sendto(self, data, address):
        if self.type == "TCP": raise Exception("Cannot 'sent to' with TCP sockets...")
        self._socket.sendto(data, address)