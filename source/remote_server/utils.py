from thread_safe_socket import ThreadSafeSocket
import time

def wait_for_connection(sock, client_label): 
    print(f"Waiting for {client_label} client to connect") 
    sock.listen(1) 
    conn, addr = sock.accept() 
    print(f"Received connection from {addr}")
    return ThreadSafeSocket.from_socket(conn), addr
