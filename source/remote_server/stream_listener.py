from thread_safe_socket import ThreadSafeSocket
import socket
import numpy as np
import threading
from utils import *
import time

def stablish_connection(server_socket, label):
    global connected_clients

    # Wait for a client to connect
    conn, addr = wait_for_connection(server_socket, label)
    with lock:
        connected_clients.add(conn)

    # Then wait another client to talk to connects
    while True:
        with lock:
            if len(connected_clients) > 1: break

        conn.send("Waiting for peer".encode())
        time.sleep(0.5)

    return conn, addr

def client_handler(server_socket, client_label):
    global connected_clients

    conn, addr = stablish_connection(server_socket, client_label)

    while True:
        try:
            data = conn.recv(4064)
            if data:
                with lock:
                    for client_conn in connected_clients:
                        if client_conn != conn: client_conn.sendall(data)

        except Exception as e:
            print(f"An error ocurred: {str(e)}, finishing connection")
            conn.close()
            with lock:
                connected_clients.remove(conn)

            # Restablish connection with car
            conn, addr = stablish_connection(server_socket, client_label)
            conn.send("ready")



if __name__ == "__main__":
    HOST = ""
    CAR_PORT = 8485
    CONTROLLER_PORT = 8486

    # Creating the sockets to listen the streamer and for retransmission
    car_socket = ThreadSafeSocket(socket.AF_INET, socket.SOCK_STREAM)
    car_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    car_socket.bind((HOST, CAR_PORT))

    controller_socket = ThreadSafeSocket(socket.AF_INET, socket.SOCK_STREAM)
    controller_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    controller_socket.bind((HOST, CONTROLLER_PORT))

    # To keep track of the state of the sockets
    lock = threading.Lock()
    connected_clients = set()


    # Create persistent handlers for the car and the controller
    car_handler = threading.Thread(target=client_handler, daemon=True, args=(car_socket,"RC-Car",))
    controller_handler = threading.Thread(target=client_handler, daemon=True, args=(controller_socket,"Remote-Controller",))

    car_handler.start()
    controller_handler.start()

    try:
        while True:
            pass
    except Exception as e:
        print(str(e))
        car_socket.close()
        controller_socket.close()
