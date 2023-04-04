import socket
import threading

class ThreadSafeSocket:
    def __init__(self, family, type):
        self._socket = socket.socket(family, type)
        self._lock = threading.Lock()

    def __getattr__(self, name):
        # delegate all other attribute access to the underlying socket object
        return getattr(self._socket, name)

    def connect(self, address):
        with self._lock:
            self._socket.connect(address)

    def listen(self, backlog):
        with self._lock:
            self._socket.listen(backlog)

    def accept(self):
        with self._lock:
            client_socket, address = self._socket.accept()
            return ThreadSafeSocket.from_socket(client_socket), address

    def send(self, data, flags=0):
        with self._lock:
            return self._socket.send(data, flags)

    def recv(self, bufsize, flags=0):
        with self._lock:
            return self._socket.recv(bufsize, flags)

    def setsockopt(self, level, option, value):
        with self._lock:
            return self._socket.setsockopt(level, option, value)

    def close(self):
        with self._lock:
            self._socket.close()

    def recvfrom(self, buffer_size):
        with self._lock:
            return self._socket.recvfrom(buffer_size)
        
    def sendto(self, data, address):
        with self._lock:
            return self._socket.sendto(data, address)

    @staticmethod
    def from_socket(sock):
        # create a new ThreadSafeSocket object from an existing socket object
        tss = ThreadSafeSocket()
        tss._socket = sock
        return tss
