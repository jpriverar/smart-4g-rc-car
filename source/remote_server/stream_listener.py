import socket
import pickle
import struct

HOST = ""
PORT = 8485

# Creating the socket to listen the stream
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))

# Only one incoming connection at a time
server_socket.listen(1)
print(f"Server listening on port {PORT}")

conn, address = server_socket.accept()
print(f"Received connection from {address}")

# To read the incoming stream of data
data = b""
payload_size = struct.calcsize(">L")

frame_counter = 0
try:
    while True:
        # Wait until the size of the data is known
        while len(data) < payload_size:
            data += conn.recv(4096)

        # Getting the size of the actual data
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack(">L", packed_msg_size)[0]

        # Waiting until all the data is received
        while len(data) < msg_size:
            data += conn.recv(4096)

        # Getting the frame
        frame_data = data[:msg_size]
        data = data[msg_size:]
        frame = pickle.loads(frame_data, encoding="bytes")

        frame_counter += 1
        print(f"frame: {frame_counter}, size: {msg_size}")

except Exception as e:
    print(str(e))
    conn.close()
    server_socket.close()
