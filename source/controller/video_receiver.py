import cv2
import numpy as np
import sys
import threading
import multiprocessing
from remote_controller import RemoteController

sys.path.insert(1, "/home/jprivera/Scripts/smart_4g_car/source/common")
from socket_relay_client import RelayClientUDP

HOST = "3.134.62.14"
CONTROL_PORT = 8486
VIDEO_PORT = 8488

control_client = RelayClientUDP(HOST, CONTROL_PORT)
control_client.sendto("OK".encode())

video_client = RelayClientUDP(HOST, VIDEO_PORT)
video_client.sendto("OK".encode())

controller = RemoteController(dev_path="/dev/input/event8", sender=control_client)
#controller_proc = multiprocessing.Process(target=controller.read_loop, daemon=True)
controller_thread = threading.Thread(target=controller.read_loop, daemon=True)
#controller_proc.start()
controller_thread.start()

max_datagram_size = 65536

while True:
    
    buffer, address = video_client.recvfrom(max_datagram_size)
    if not buffer: continue
    
    #if len(data) < 100:
    #    packets = int.from_bytes(data, byteorder="big")

    #    buffer = b""
    #    for i in range(packets):
    #        data, address = video_client._socket.recvfrom(max_datagram_size)
    #        buffer += data

    # Decoding the image
    frame = cv2.imdecode(np.frombuffer(buffer, dtype=np.uint8), cv2.IMREAD_COLOR)

    if frame is not None:
        cv2.imshow("frame", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    pass
    

cv2.destroyAllWindows()
    