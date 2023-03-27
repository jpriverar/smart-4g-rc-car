import socket
import numpy as np
import threading

HOST = ""
SOURCE_PORT = 8485
DEST_PORT = 8486

# Creating the socket to listen the streamer
source_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
source_socket.bind((HOST, SOURCE_PORT))

dest_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
dest_socket.bind((HOST, DEST_PORT))

# Only one incoming connection at a time
source_socket.listen(1)
dest_socket.listen(1)
print(f"Source listening on port {SOURCE_PORT}")
print(f"Destination listening on port {DEST_PORT}")

source_conn, source_address = source_socket.accept()
print(f"Received connection from {source_address}")
dest_conn, dest_address = dest_socket.accept()
print(f"Received connection from {dest_address}")

try:
    while True:
       data = source_conn.recv(4096)
       if data:
          dest_conn.sendall(data)

except Exception as e:
   print(str(e))
   source_conn.close()
   dest_conn.close()
   source_socket.close()
   dest_socket.close()
