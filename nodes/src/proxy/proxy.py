from select import select
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

from nodes.src.node.exit_node_protocol import make_request_to_end_point


def sys_append_modules() -> None:
    """
    Appends all important modules into sys_path.
    :returns: None.
    """
    parent = '../../../...'
    module = os.path.abspath(os.path.join(os.path.dirname(__file__), parent))
    sys.path.append(module)


sys_append_modules()

from nodes.src.construct_messages import *
from nodes.src.client.client import Client

from toralina_common.load_json import load_proxy
from socket import *

BUFF = 1024


class Proxy:
    def __init__(self, client: Client):
        self.__proxy_address = load_proxy()
        self.__socket = socket(AF_INET, SOCK_STREAM)
        self.__socket.bind(self.__proxy_address)
        self.__circuit = client.get_circuit()
        self.__keys = client.get_keys()
        self.__circuit_id = client.get_circuit_id()
        self.__client_socket = client.get_client_socket()

    def __interpret_https_request(self, msg):
        msg = msg.replace("\r", "")

        split_msg = msg.split("\n")

        url = split_msg[0].split(" ")[1]

        headers = split_msg[1:len(split_msg) - 2]
        header_names = []
        header_values = []

        for header in headers:
            header_name = header.split(": ")[0]
            header_value = header.split(": ")[1]

            if header_name != "is_toralina" and header_name != "Host" and header_name != "Proxy-Connection":
                header_names.append(header_name)
                header_values.append(header_value)

        post_data = b""

        return url, header_names, header_values, post_data

    def handle_toralina_message(self, msg: str, s: socket):
        url, header_names, header_values, post_data = self.__interpret_https_request(msg)

        msg_data = get_network_msg_data(url, header_names, header_values, post_data)
        network_msg = get_network_msg(self.__circuit_id, msg_data, self.__keys, "yes")

        network_msg_split = network_msg.split("#-#")
        len_of_prefix = len("".join(network_msg_split[:3])) + 9

        self.__client_socket.settimeout(2)

        if len(network_msg_split[3]) > 1024 - len_of_prefix:
            while msg_data:
                network_msg = get_network_msg(self.__circuit_id, msg_data[:int(BUFF / 64)], self.__keys, "yes")
                network_msg = network_msg + "PADDING" + "A" * (BUFF - len(network_msg) - 7)
                if len(network_msg) != 1024:
                    print("MESSAGE: " + network_msg + " LENGTH: " + str(len(network_msg)))
                self.__client_socket.send(network_msg.encode('utf-8'))
                if len(msg_data) < BUFF / 64:
                    break
                msg_data = msg_data[int(BUFF / 64):]
            end_msg = get_end_network_msg(self.__circuit_id, self.__keys, "yes")
            self.__client_socket.send(end_msg.encode('utf-8'))
        else:
            self.__client_socket.send(network_msg.encode('utf-8'))
            end_msg = get_end_network_msg(self.__circuit_id, self.__keys, "yes")
            self.__client_socket.send(end_msg.encode('utf-8'))

        try:
            response = self.__client_socket.recv(BUFF)
            full_data = ""
            while response:
                html_data = response.decode('utf-8').split("#-#")[3].split("PADDING")[0]
                if html_data == " ":
                    break
                html_data = decrypt_string(html_data.encode('utf-8'), self.__keys)
                full_data += html_data
                response = self.__client_socket.recv(BUFF)
        except:
            return

        print(full_data)

        s.send(full_data.encode('utf-8'))

    def handle_normal_message(self, msg, s):
        url, header_names, header_values, post_data = self.__interpret_https_request(msg)

        headers = {}

        for i in range(len(header_names)):
            headers[header_names[i]] = header_values[i]

        response = make_request_to_end_point(url, headers, post_data)

        if response:
            response = response.encode('utf-8')
        else:
            response = b''

        s.send(response)

    def listen_for_requests(self):
        self.__socket.listen()

        inputs = [self.__socket]
        outputs = []

        while True:
            readable, writable, exceptions = select(inputs, outputs, inputs)
            for s in readable:
                try:
                    if s is self.__socket:
                        conn = s.accept()[0]
                        inputs.append(conn)
                    else:
                        msg = s.recv(BUFF * 256).decode('utf-8')
                        if msg:
                            print("\nRecieved MSG: " + msg)
                            if "is_toralina" in msg:
                                self.handle_toralina_message(msg, s)
                                print("toralina MSG")
                            else:
                                self.handle_normal_message(msg, s)
                        else:
                            s.close()
                            inputs.remove(s)
                except ConnectionError:
                    print("Connection Error")
                    s.close()
                    inputs.remove(s)