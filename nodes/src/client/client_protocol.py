import random
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
from client import Client
import string

CIRCUIT_ID_LENGTH = 15


def choose_circuit(client: Client) -> list:
    client_node = client.get_node()
    node_list = client_node.get_this_node_list()

    if len(node_list) < 3:
        return []

    client_node_socket = client_node.get_node_socket().getsockname()
    if client_node_socket in node_list:
        node_list.remove(client_node_socket)
    return sorted(node_list, key=lambda x: random.randint(1, 10))[:3]


def generate_id() -> str:
    letters = string.ascii_lowercase
    return ''.join([random.choice(letters) for i in range(CIRCUIT_ID_LENGTH)])


def inform_circuit(circuit: list, client_socket: socket, circuit_id: str):
    for i in range(3):
        prev_node = circuit[max(i-1, 0)] if i != 0 else ["", ""]
        next_node = circuit[min(i + 1, 2)] if i != 2 else ["", ""]
        msg_list = [prev_node, next_node]

        inform_msg = ((str(i) + " " + " ".join(list(map(lambda x: x[0] + "-" + x[1], msg_list))) + " " + circuit_id)
                      .encode("utf-8"))

        client_socket.connect(circuit[i])
        client_socket.send(inform_msg)


def initiate_client() -> list:
    client = Client()
    circuit = choose_circuit(client)
    circuit_id = generate_id()

    inform_circuit(circuit, client.get_client_socket(), circuit_id)

    return circuit
