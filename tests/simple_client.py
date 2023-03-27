import socket

HOST = "3.134.62.14"
PORT = 8485

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

msg = "hello hello!"
client_socket.send(msg.encode("utf-8"))

msg = client_socket.recv(1024).decode("utf-8")
print(msg)

client_socket.close()