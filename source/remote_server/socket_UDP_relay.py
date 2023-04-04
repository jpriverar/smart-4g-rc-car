import socket
import select

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

    HOST = ''
    CAR_PORT = 8485
    CONTROLLER_PORT = 8486

    car_socket, controller_socket = start_server(HOST, CAR_PORT, CONTROLLER_PORT)

    car_address = None
    controller_address = None

    while True:
        # Getting sockets with something to receive
        ready_to_read, _, _ = select.select([car_socket, controller_socket], [], [], 0)
        if not ready_to_read: continue

        for sock in ready_to_read:
            if sock == car_socket:
                data, car_address = car_socket.recvfrom(4064)
                print(f"Received car data from: {car_address}")
                print(data.decode('utf-8'))
                if data and controller_address:
                    controller_socket.sendto(data, controller_address)

            if sock == controller_socket:
                data, controller_address = controller_socket.recvfrom(1024)
                print(f"Received controller data from: {controller_address}")
                print(data.decode('utf-8'))
                if data and car_address:
                    car_socket.sendto(data, car_address)
