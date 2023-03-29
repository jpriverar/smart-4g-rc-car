import socket
import select

def start_server(host, car_port, controller_port):
    # Creating the socket objects
    car_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    car_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    controller_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    controller_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind sockets to host and port numbers
    car_socket.bind((host, car_port))
    controller_socket.bind((host, controller_port))

    # Listen for incoming connections
    car_socket.listen(1)
    controller_socket.listen(1)

    return car_socket, controller_socket

def stablish_connection(car_socket, controller_socket):
    # Accept connections from clients
    print("Waiting for RC-Car client...")
    car_conn, car_addr = car_socket.accept()
    print(f"RC-Car Client connected: {car_addr}")

    print("Waiting for Remote-Controller client...")
    controller_conn, controller_addr = controller_socket.accept()
    print(f"Remote-Controller Client connected: {controller_addr}")

    return car_conn, controller_conn

def start_relay(car_socket, controller_socket):
    car_conn, controller_conn = stablish_connection(car_socket, controller_socket)
    car_conn.sendall("OK".encode())
    controller_conn.sendall("OK".encode())
    return car_conn, controller_conn


if __name__ == "__main__":

    HOST = ''
    CAR_PORT = 8485
    CONTROLLER_PORT = 8486

    car_socket, controller_socket = start_server(HOST, CAR_PORT, CONTROLLER_PORT)

    # Wait for both sides to be connected
    car_conn, controller_conn = start_relay(car_socket, controller_socket)
    connected_sockets = [car_conn, controller_conn]

    # Indefinite socket relay
    try:
        while True:
            # Getting sockets with something to receive
            read_sockets, _, _ = select.select(connected_sockets, [], [])
            for sock in read_sockets:
                if sock == car_conn:
                    data = car_conn.recv(4064)
                    if data:
                        controller_conn.sendall(data)

                    else: # Connection with car lost
                        car_conn.close()
                        controller_conn.close()
                        car_conn, controller_conn = start_relay(car_socket, controller_socket)
                        connected_sockets = [car_conn, controller_conn]
                        break

                if sock == controller_conn:
                    data = controller_conn.recv(1024)
                    if data:
                        car_conn.sendall(data)

                    else: # Connection with controller lost
                        controller_conn.close()
                        car_conn.close()
                        car_conn, controller_conn = start_relay(car_socket, controller_socket)
                        connected_sockets = [car_conn, controller_conn]
                        break

    except Exception as e:
        print("Something happened: " + str(e))
        car_conn.close()
        controller_conn.close()

        car_socket.close()
        controller_socket.close()
