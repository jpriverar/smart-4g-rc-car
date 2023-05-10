#! /usr/bin/python

import socket
import select
import argparse

def start_server(host, car_port, controller_port):
    # Creating the socket objects
    car_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    car_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    controller_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    controller_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind sockets to host and port numbers
    car_socket.bind((host, car_port))
    controller_socket.bind((host, controller_port))

    return car_socket, controller_socket

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--car", type=int, required=True)
    parser.add_argument("--controller", type=int, required=True)
    args = parser.parse_args()

    HOST = ''
    car_socket, controller_socket = start_server(HOST, args.car, args.controller)

    car_address = None
    controller_address = None

    while True:
        # Getting sockets with something to receive
        ready_to_read, _, _ = select.select([car_socket, controller_socket], [], [], 0)
        if not ready_to_read: continue

        for sock in ready_to_read:
            if sock == car_socket:
                data, car_address = car_socket.recvfrom(65536)
                print(f"Got {len(data)} bytes of data from {car_address}")
                if controller_address:
                    controller_socket.sendto(data, controller_address)

            if sock == controller_socket:
                data, controller_address = controller_socket.recvfrom(1024)
                print(f"Got {len(data)} bytes of data from {controller_address}")
                if car_address:
                    car_socket.sendto(data, car_address)
