import socket

class SocketRelayClient:
    def __init__(self):
        self.connected = False

    def connect(self, host, port):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
                data = self._socket.recv(buffer_size)
                if not data:
                    raise Exception
                return data

            except Exception as e:
                print("Something went wrong: " + str(e))
                self._socket.close()
                self.connected = False
