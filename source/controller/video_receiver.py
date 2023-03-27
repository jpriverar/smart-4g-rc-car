import cv2
import numpy as np
import socket

HOST = "3.134.62.14"
PORT = 8486

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

while True:
    # Getting the size of the image
    size_data = client_socket.recv(4)
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

client_socket.close()
cv2.destroyAllWindows()
    