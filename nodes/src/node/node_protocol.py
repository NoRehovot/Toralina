import os
import sys


def sys_append_modules() -> None:
    """
    Appends all important modules into sys_path.
    :returns: None.
    """
    parent = '../../../...'
    module = os.path.abspath(os.path.join(os.path.dirname(__file__), parent))
    sys.path.append(module)


sys_append_modules()

from nodes.src.node.node import Node
import select
from nodes.src.construct_messages import *
from nodes.src.node.dir_communication import get_client_from_name
from toralina_common.ip_utils import send_message, get_free_port_socket
from nodes.src.file_operations import send_file_msg, receive_file_msg


BUFF = 1024  # buffer size for socket communication


def interpret_circuit_msg(msg):
    split_msg = msg.split("#-#")
    circuit_id = split_msg[0]
    command = split_msg[1]
    last_signal = split_msg[2]
    data = split_msg[3]
    return circuit_id, last_signal, command, data


def pass_confirm_msg(response, from_socket, id_to_key):
    circuit_id, last_signal, command, data = interpret_circuit_msg(response)
    response = get_confirm_msg(circuit_id, data, [id_to_key[circuit_id]])
    from_socket.send(response.encode('utf-8'))


def handle_file_msg(node_socket, id_to_circuit, circuit_id, last_signal, data, id_to_key, from_socket):
    print("INFO: received file msg")

    file_msg_data = decrypt_string(data, [id_to_key[circuit_id]])

    from_socket.send(" ".encode('utf-8'))

    file_data = receive_file_msg(from_socket, [id_to_key[circuit_id]])

    last_signal = decrypt_string(last_signal.encode('utf-8'), [id_to_key[circuit_id]])

    if last_signal == "yes":
        print("\nLAST NODE\n")
        filename, dest, src = unpack_msg_data(file_msg_data)

        client_data = get_client_from_name(dest)

        s = send_file_msg(file_data, file_msg_data, [], circuit_id, client_data, last_signal)
        print("Sent File")
        response = s.recv(BUFF).decode('utf-8')
        print("RESPONSE: " + response)
        pass_confirm_msg(response, from_socket, id_to_key)
    else:
        s = send_file_msg(file_data, file_msg_data, [], circuit_id, id_to_circuit[circuit_id], last_signal)
        response = s.recv(BUFF).decode('utf-8')
        pass_confirm_msg(response, from_socket, id_to_key)

    return id_to_circuit, id_to_key


def handle_add_node(node_socket, id_to_circuit, circuit_id, last_signal, data, id_to_key, from_socket):
    print("INFO: received add node msg")
    if circuit_id in id_to_circuit.keys():
        data = decrypt_string(data.encode('utf-8'), [id_to_key[circuit_id]])
        last_signal = decrypt_string(last_signal.encode('utf-8'), [id_to_key[circuit_id]])
        if last_signal == "yes":
            new_node = data.split(" ")
            new_node = (new_node[0], int(new_node[1]))
            add_node_msg = get_add_node_msg(circuit_id, data, [], last_signal)
            response = send_message(add_node_msg.encode('utf-8'), new_node)  # send forward and get confirmation

            print("INFO: got confirmation for added node")
            pass_confirm_msg(response, from_socket, id_to_key)  # pass confirmation back to client

            id_to_circuit[circuit_id] = new_node
        else:
            next_node = id_to_circuit[circuit_id]
            add_node_msg = get_add_node_msg(circuit_id, data, [], last_signal)
            response = send_message(add_node_msg.encode('utf-8'), next_node)  # send forward and get confirmation

            print("INFO: got confirmation for added node")
            pass_confirm_msg(response, from_socket, id_to_key)  # pass confirmation back to client
    else:
        id_to_circuit[circuit_id] = (None, None)
        response = get_confirm_msg(circuit_id,  " ".join([node_socket.getsockname()[0], str(node_socket.getsockname()[1])]), [])
        from_socket.send(response.encode('utf-8'))
        print("INFO: added circuit to dictionary")

    return id_to_circuit, id_to_key


def handle_add_key(node_socket, id_to_circuit, circuit_id, last_signal, data, id_to_key, from_socket):
    print("INFO: received add key msg")
    if last_signal == "yes":
        id_to_key[circuit_id] = data.encode('utf-8')
        print("INFO: added key to dictionary")
        response = get_confirm_msg(circuit_id,
                                   " ".join([node_socket.getsockname()[0], str(node_socket.getsockname()[1])]), [id_to_key[circuit_id]])
        from_socket.send(response.encode('utf-8'))
    else:
        data = decrypt_string(data.encode('utf-8'), [id_to_key[circuit_id]])
        last_signal = decrypt_string(last_signal.encode('utf-8'), [id_to_key[circuit_id]])
        next_node = id_to_circuit[circuit_id]
        add_key_msg = get_send_key_msg(circuit_id, data, [], last_signal)
        response = send_message(add_key_msg.encode('utf-8'), next_node)  # send forward and get confirmation

        print("INFO: got confirmation for added key")
        pass_confirm_msg(response, from_socket, id_to_key)  # pass confirmation back to client

    return id_to_circuit, id_to_key


def handle_message(node_socket, id_to_circuit, circuit_id, last_signal, command, data, command_to_function, id_to_key, from_socket):
    try:
        to_execute = command_to_function[command]
        id_to_circuit, id_to_key = to_execute(node_socket, id_to_circuit, circuit_id, last_signal, data, id_to_key, from_socket)
    except KeyError:
        return id_to_circuit, id_to_key
    return id_to_circuit, id_to_key


def main_node_loop():
    node = Node()
    node_socket = node.get_node_socket()
    node_socket.listen()

    inputs = [node_socket]
    outputs = []
    id_to_circuit = {

    }
    id_to_key = {

    }
    command_to_function = {
        "1": handle_add_node,
        "2": handle_add_key,
        "3": handle_file_msg
    }

    while True:
        readable, writable, exceptions = select.select(inputs, outputs, inputs)
        for s in readable:
            try:
                if s is node_socket:
                    conn = s.accept()[0]
                    inputs.append(conn)
                else:
                    msg = s.recv(BUFF).decode('utf-8')
                    print("\nReceived MSG: " + msg)
                    if msg:
                        try:
                            circuit_id, last_signal, command, data = interpret_circuit_msg(msg)
                            if command != '4':
                                id_to_circuit, id_to_key = handle_message(node_socket, id_to_circuit, circuit_id,
                                                                          last_signal, command,
                                                                          data, command_to_function, id_to_key, s)
                        except IndexError:
                            print("Connection Ended")
                    else:
                        s.close()
                        inputs.remove(s)
            except ConnectionError:
                print("Connection Error")
                s.close()
                inputs.remove(s)
