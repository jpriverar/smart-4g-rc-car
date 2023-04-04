import cv2
import numpy as np
import sys
import threading
from remote_controller import RemoteController

sys.path.insert(1, "/home/jprivera/Scripts/smart_4g_car/source/common")
from socket_relay_client import RelayClientUDP

HOST = "3.134.62.14"
PORT = 8486

client = RelayClientUDP(HOST, PORT)
client.sendto("OK".encode())

controller = RemoteController(dev_path="/dev/input/event6", sender=client)
controller_thread = threading.Thread(target=controller.read_loop, daemon=True)
controller_thread.start()

while True:
    # Getting the size of the image
    size_data = client._socket.recvfrom(4)
    size = int.from_bytes(size_data, byteorder="big")

    # Waiting to get the whole image
    data = b""
    while len(data) < size:
        data += client._socket.recvfrom(size - len(data))

    # Decoding the image
    frame = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
    cv2.imshow("frame", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
    