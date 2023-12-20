from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
from ..node.node import Node
import random
from toralina_common.ip_utils import get_this_ip


def check_if_node_is_client(node_ip):
    return node_ip == get_this_ip()


def get_three_nodes():
    """
    :return: 3 random nodes from ds node_list OR an empty list if there are less than four nodes available
    """
    n = Node()
    node_list = n.get_this_node_list()

    if len(node_list) <= 3:
        return []

    index1 = random.randint(len(node_list))
    while check_if_node_is_client(node_list[index1][0]):
        index1 = random.randint(len(node_list))

    index2 = random.randint(len(node_list))
    while index2 == index1 or check_if_node_is_client(node_list[index1][0]):
        index2 = random.randint(len(node_list))

    index3 = random.randint(len(node_list))
    while index3 == index1 or index3 == index2s or check_if_node_is_client(node_list[index1][0]):
        index3 = random.randint(len(node_list))

    return [node_list[index1], node_list[index2], node_list[index3]]


def inform_nodes(nodes_to_use):
    pass
