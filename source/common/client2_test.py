from socket_relay_client import SocketRelayClient
import time

HOST = "3.134.62.14"
PORT = 8486

client = SocketRelayClient(type="UDP")

# Sending message just so that relay server knows we are here
client.sendto("Ready".encode(), (HOST, PORT))

while True:
        client.sendto("Hello from client2".encode(), (HOST, PORT))
        time.sleep(3)