from socket_relay_client import SocketRelayClient

HOST = "3.134.62.14"
PORT = 8485

client = SocketRelayClient()

while True:
    if client.connected:
        data = client.recv(1024)
        if data:
            msg = data.decode('utf-8')
            print(msg)
    else:
        client.connect(HOST, PORT)