from .directory_server import DirectoryServer
BUFF = 1024  # buffer size for socket communication

"""
Dictionary for associating each number code that can be sent by a node
with a function to be executed (see dir_communication.py)
"""
POSSIBLE_ACTIONS = {

}


def node_list_to_string(node_list):
    return " ".join(list(map(lambda x: x[0] + "-" + str(x[1]), node_list)))


def send_node_list(client_data):
    """
    Parameters: the client details
    Returns: None

    This function responds to the client with the node_list
    """
    ds = DirectoryServer()
    msg = node_list_to_string(ds.get_node_list())
    client_data[0].send(msg.encode('utf-8'))


def check_code_num(code_num):
    """
    Parameters: code_num (string)
    Returns: None / code_num

    This function checks whether a client request is valid
    """
    if code_num not in POSSIBLE_ACTIONS.keys():
        return None
    return code_num


def parse_args(msg):
    """
    Parameters: client message
    Returns: tuple with the code number and node address

    This function parses client message arguments
    """
    code_num = check_code_num(msg[0])
    client_address = (msg[1], int(msg[2]))
    return code_num, client_address


def listen_for_requests(ds_socket):
    """
    Parameters: the directory server socket
    Returns: the request the client sent

    This function is responsible for listening to client requests and finding out what they want
    """
    conn, addr = ds_socket.accept()
    with conn:
        data = conn.recv(BUFF)
        if data:
            data = data.decode('utf-8').split(" ")
            code_num, node_address = parse_args(data)
            if code_num:
                POSSIBLE_ACTIONS[code_num]((conn, node_address))


def initiate_ds():
    """
    Parameters: -
    Returns: None

    This function creates the ds object and handles all its communication with nodes
    """

    ds = DirectoryServer()

    # set the POSSIBLE_ACTIONS dictionary
    global POSSIBLE_ACTIONS
    POSSIBLE_ACTIONS = {
        '0': send_node_list,
        '1': ds.append_node_list,
        '2': ds.remove_from_node_list
    }

    ds_socket = ds.get_ds_socket()
    ds_socket.listen()

    while True:
        listen_for_requests(ds_socket)
