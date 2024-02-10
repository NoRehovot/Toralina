from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM

BUFF = 1024  # buffer size for socket communication


def parse_circuit_data(data: str) -> {}:
    data = data.split(" ")
    return {
        'pos': data[0],
        'prev': data[1].split("-") if int(data[0]) > 0 else None,
        'next': data[len(data) - 2].split("-") if int(data[0]) < 2 else None,
        'circuit_id': data[len(data) - 1]
    }


def listen_for_circuit_initiation(node_socket: socket):
    node_socket.listen()
    conn, addr = node_socket.accept()

    with conn:
        data = conn.recv(BUFF)
        circuit_info = parse_circuit_data(data.decode('utf-8'))

    return circuit_info, addr
