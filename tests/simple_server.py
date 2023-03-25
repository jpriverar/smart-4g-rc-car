import socket

HOST = "0.0.0.0" # On all interfaces
PORT = 8485

# Creating socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))

# Start listening on incoming connections
server_socket.listen(5)
print(f"Server listening on port {PORT}")

while True:
    # Wait for a client to connect
    client_socket, client_address = server_socket.accept()
    print(f"Received connection from {client_address}")

    # Read data from the client
    data = client_socket.recv(1024)  # Read up to 1024 bytes
    message = data.decode('utf-8')
    print(f"Received message from {client_address}: {message}")

    # Close the client socket
    client_socket.close()