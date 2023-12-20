from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
from node import Node


def listen_for_client():
    n = Node()
    node_socket = n.get_node_socket()
    node_socket.listen()
    conn, addr = node_socket.accept()

    with conn:
        data = conn.recv(BUFF)
        if data:
            data = data.decode('utf-8').split(" ")
