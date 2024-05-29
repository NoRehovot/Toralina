import random
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
from nodes.src.client.client import Client
import string
from nodes.src.construct_messages import *
from nodes.src.node.node_protocol import interpret_circuit_msg
from cryptography.fernet import Fernet
from toralina_common.ip_utils import get_free_port_socket
import select
import pathlib
from nodes.src.file_operations import send_file_msg, receive_file_msg
from nodes.src.view import ClientView

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
    with get_free_port_socket() as s:
        s.connect(circuit[0])
        for i in range(3):
            # add node
            add_node_data = get_add_node_data(circuit[i])
            add_node_msg = get_add_node_msg(circuit_id, add_node_data, keys, "yes")

            s.send(add_node_msg.encode('utf-8'))
            response = s.recv(BUFF)

            new_key = Fernet.generate_key()
            add_key_msg = get_send_key_msg(circuit_id, new_key.decode('utf-8'), keys, "yes")

            s.send(add_key_msg.encode('utf-8'))
            response = s.recv(BUFF)

            keys.append(new_key)
            print(f"Added Node {i+1} to circuit")

    client.set_keys(keys)


def handle_file_sent(from_socket, client, data, cv: ClientView):
    from_socket.send(" ".encode('utf-8'))

    file_content = receive_file_msg(from_socket, [])

    filename, dest, src = unpack_msg_data(data)

    print(filename, file_content)

    write_file(filename, file_content)
    print("wrote File")
    cv.update_file_list()
    cv.update_client_messages(src, f"{src}: Sent a File ({filename})")

    from_socket.send(get_confirm_msg(client.get_circuit_id(), " ", []).encode('utf-8'))


def listen_for_files(client, cv):
    main_socket = client.get_client_socket()
    print(main_socket.getsockname())
    main_socket.listen()

    inputs = [main_socket]
    outputs = []

    while True:
        readable, writable, exceptions = select.select(inputs, outputs, inputs)
        for s in readable:
            try:
                if s is main_socket:
                    print("Connection")
                    conn = s.accept()[0]
                    inputs.append(conn)
                else:
                    msg = s.recv(BUFF).decode('utf-8')
                    print("\nRecieved MSG: " + msg)
                    try:
                        circuit_id, last_signal, command, data = interpret_circuit_msg(msg)
                        if command == '3':
                            handle_file_sent(s, client, data, cv)
                    except IndexError:
                        print("Connection Ended")
                        s.close()
                        inputs.remove(s)
            except ConnectionError:
                print("Connection Error")
                s.close()
                inputs.remove(s)


def send_file(file_location, dest, client, src):
    filename = file_location.split("/")[len(file_location.split("/"))-1]
    print("SENDING " + filename)
    file_content = read_file(file_location)

    file_msg_data = get_file_msg_data(filename, dest, src)

    s = send_file_msg(file_content, file_msg_data, client.get_keys(), client.get_circuit_id(), client.get_circuit()[0])

    # response = s.recv(BUFF).decode("utf-8")
    #
    # if response.split("#-#")[1] == '0':
    #     print("GOT RESPONSE")
    #
    # return response


def read_file(file_location):
    with open(file_location, 'rb') as f:
        return f.read()


def write_file(file_name, file_content):
    root = pathlib.Path(__file__).parent.resolve()
    path = f"{root}\\client_files\\{file_name}"
    with open(path, 'wb') as f:
        f.write(file_content)


def initiate_client(client):
    client_socket = client.get_client_socket()

    circuit = choose_circuit(client)
    if circuit:
        print("Found Circuit")
        circuit_id = generate_id()
        client.set_circuit_id(circuit_id)

        inform_circuit(client, circuit, client_socket, circuit_id)

        client.set_circuit(circuit)
