import random
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
from nodes.src.client.client import Client
import string
from nodes.src.construct_messages import *
from cryptography.fernet import Fernet

CIRCUIT_ID_LENGTH = 15
BUFF = 1024


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


def inform_circuit(client: Client, circuit: list, client_socket: socket, circuit_id: str):
    keys = []
    for i in range(3):
        # add node
        add_node_data = get_add_node_data(circuit[i])
        add_node_msg = get_add_node_msg(circuit_id, add_node_data, keys, "yes")

        client_socket.send(add_node_msg.encode('utf-8'))
        response = client_socket.recv(BUFF)

        new_key = Fernet.generate_key()
        add_key_msg = get_send_key_msg(circuit_id, new_key.decode('utf-8'), keys, "yes")

        client_socket.send(add_key_msg.encode('utf-8'))
        response = client_socket.recv(BUFF)

        keys.append(new_key)
        print(f"Added Node {i+1} to circuit")

    client.set_keys(keys)


def initiate_client(client):
    circuit = choose_circuit(client)
    if circuit:
        print("Found Circuit")
        circuit_id = generate_id()
        client.set_circuit_id(circuit_id)

        client_socket = client.get_client_socket()
        client_socket.connect(circuit[0])

        inform_circuit(client, circuit, client_socket, circuit_id)

        client.set_circuit(circuit)
