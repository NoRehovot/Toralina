from toralina_common import load_json, ip_utils

"""
This file is for communicating with the directory server

There will be 3 kinds of requests from a client to a directory server:
0 - Ask the DS to respond with the active nodes list
1 - Ask the DS to add a node to the nodes list
2 - Ask the DS to remove a node from the nodes list
"""

DS_ADDR = load_json.load_config()  # the DS ip and port
BUFF = 1024  # buffer size for socket communication


def update_node_list(node, code_num):
    """
    Parameters: Node object
    Returns: None

    This function tells the directory server that a new node is up
    """
    s = ip_utils.get_free_port_socket()
    s.connect(DS_ADDR)

    node_addr = node.get_node_socket().getsockname()

    msg = str(code_num) + " " + node_addr[0] + " " + str(node_addr[1])

    s.send(msg.encode('utf-8'))
    s.close()


def node_list_to_list(node_list_str):
    return list(map(lambda x: (x[0], int(x[1])), list(map(lambda x: tuple(x.split("-")), node_list_str.split(" ")))))


def get_node_list(node):
    """
    Parameters: -
    Returns: the node list

    This function gets the list of running nodes from the ds
    """
    s = ip_utils.get_free_port_socket()
    s.connect(DS_ADDR)

    node_addr = node.get_node_socket().getsockname()

    msg = "0 " + node_addr[0] + " " + str(node_addr[1])

    s.send(msg.encode('utf-8'))
    data = s.recv(BUFF).decode('utf-8')
    node_list = node_list_to_list(data)
    s.close()
    return node_list
