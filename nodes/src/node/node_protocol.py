from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
from node import Node
import select
from nodes.src.construct_messages import *
from toralina_common.ip_utils import send_message, get_free_port_socket
from exit_node_protocol import make_request_to_end_point

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


def handle_network_msg(node_socket, id_to_circuit, circuit_id, last_signal, data, id_to_key, from_socket):
    print("INFO: received network msg")
    if "PADDING" in data:
        data = data.split("PADDING")[0]
    try:
        data = decrypt_string(data.encode('utf-8'), [id_to_key[circuit_id]])
    except KeyError:
        response = get_confirm_msg(circuit_id, " ", [])
        from_socket.send(response.encode('utf-8'))
        print("sent response")
        return id_to_circuit, id_to_key
    last_signal = decrypt_string(last_signal.encode('utf-8'), [id_to_key[circuit_id]])
    if last_signal == "yes":
        from_socket.settimeout(2)
        all_data = ""
        while data != " ":
            all_data += data
            try:
                interpreted_msg = interpret_circuit_msg(from_socket.recv(BUFF).decode('utf-8'))
            except IndexError:
                break
            except:
                break
            if interpreted_msg[2] == '4':
                break
            data = decrypt_string(interpreted_msg[3].encode('utf-8'), [id_to_key[circuit_id]])

        try:
            url, headers, post_data = unpack_network_msg_data(all_data)
        except IndexError:
            url, headers, post_data = None, None, None
        print("\nMESSAGE DATA:")
        print(url, headers, post_data)

        if post_data:
            post_data = post_data.encode('utf-8')

        try:
            html_data = make_request_to_end_point(url, headers, post_data)
        except:
            html_data = None

        print("\nRESPONSE DATA:")
        print(html_data)
        try:
            html_data = html_data.decode('utf-8')
        except:
            html_data = str(html_data)
        if html_data:
            while data:
                confirm_msg = get_confirm_msg(circuit_id, html_data[:int(BUFF/8)], [id_to_key[circuit_id]])
                confirm_msg = confirm_msg + "PADDING" + "A" * (BUFF - len(confirm_msg) - 7)
                from_socket.send(confirm_msg.encode('utf-8'))
                if len(html_data) < BUFF/8:
                    break
                html_data = html_data[int(BUFF/8):]
            response = get_confirm_msg(circuit_id, " ", [])
            from_socket.send(response.encode('utf-8'))
            print("sent response")

        else:
            response = get_confirm_msg(circuit_id, " ", [])
            from_socket.send(response.encode('utf-8'))
            print("sent response")
    else:
        next_node = id_to_circuit[circuit_id]
        network_msg = get_network_msg(circuit_id, data, [], last_signal)

        with get_free_port_socket() as s:
            s.connect(next_node)
            s.send(network_msg.encode('utf-8'))

            while True:
                next_msg = from_socket.recv(BUFF).decode('utf-8')
                circuit_id, last_signal, command, data = interpret_circuit_msg(next_msg)
                try:
                    last_signal = decrypt_string(last_signal.encode('utf-8'), [id_to_key[circuit_id]])
                except KeyError:
                    next_network_msg = get_end_network_msg(circuit_id, [], last_signal)
                    s.send(next_network_msg.encode('utf-8'))
                    break
                if command == '4':
                    next_network_msg = get_end_network_msg(circuit_id, [], last_signal)
                    s.send(next_network_msg.encode('utf-8'))
                    break

                if "PADDING" in data:
                    data = data.split("PADDING")[0]

                data = decrypt_string(data.encode('utf-8'), [id_to_key[circuit_id]])
                next_network_msg = get_network_msg(circuit_id, data, [], last_signal)
                next_network_msg = next_network_msg + "PADDING" + "A" * (BUFF - len(next_network_msg) - 7)
                s.send(next_network_msg.encode('utf-8'))

            print("Receiving data")

            s.settimeout(2)
            try:
                response = s.recv(BUFF).decode('utf-8')
                while response:
                    circuit_id, last_signal, command, data = interpret_circuit_msg(response)
                    if data == " ":
                        from_socket.send(response.encode('utf-8'))
                        break
                    data = data.split("PADDING")[0]
                    confirm_msg = get_confirm_msg(circuit_id, data, [id_to_key[circuit_id]])
                    confirm_msg = confirm_msg + "PADDING" + "A" * (BUFF - len(confirm_msg) - 7)
                    from_socket.send(confirm_msg.encode('utf-8'))
                    response = s.recv(BUFF).decode('utf-8')
            except:
                s.close()

        print("INFO: got confirmation for network msg")

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
        "3": handle_network_msg
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
                    print("\nRecieved MSG: " + msg)
                    if msg:
                        try:
                            circuit_id, last_signal, command, data = interpret_circuit_msg(msg)
                        except IndexError:
                            print("hi")
                        if command != '4':
                            id_to_circuit, id_to_key = handle_message(node_socket, id_to_circuit, circuit_id, last_signal, command,
                                                                      data, command_to_function, id_to_key, s)
                    else:
                        s.close()
                        inputs.remove(s)
            except ConnectionError:
                print("Connection Error")
                s.close()
                inputs.remove(s)
