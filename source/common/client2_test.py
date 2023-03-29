from socket_relay_client import SocketRelayClient
import time

HOST = "3.134.62.14"
PORT = 8486

client = SocketRelayClient()

while True:
    if client.connected:
        client.sendall("Hello there!".encode())
        time.sleep(3)
    else:
        client.connect(HOST, PORT)