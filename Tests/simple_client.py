import socket

HOST = "10.62.73.3"
PORT = 8485

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

msg = "hello hello!"
client_socket.send(msg.encode("utf-8"))

client_socket.close()