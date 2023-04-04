from socket_relay_client import SocketRelayClient

HOST = "3.134.62.14"
PORT = 8485

client = SocketRelayClient(type="UDP")

# Sending message just so that relay server knows we are here
client.sendto("Ready".encode(), (HOST, PORT))

while True:
    data, address = client.recvfrom(1024)
    if data:
        msg = data.decode('utf-8')
        print(msg)