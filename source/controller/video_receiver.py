import cv2
import numpy as np
import socket

sys.path.insert(1, "/home/jp/Projects/smart-4g-rc-car/source/common")
from socket_relay_client import SocketRelayClient

HOST = "3.134.62.14"
PORT = 8486

client = SocketRelayClient()

while True:
    if client.connected:
        # Getting the size of the image
        size_data = client.recv(4)
        size = int.from_bytes(size_data, byteorder="big")

        # Waiting to get the whole image
        data = b""
        while len(data) < size:
            data += client_socket.recv(size - len(data))

        # Decoding the image
        frame = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)

        cv2.imshow("frame", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        client.connect(HOST, PORT)

cv2.destroyAllWindows()
    