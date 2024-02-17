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

from toralina_common.singleton import Singleton
import toralina_common.load_json as load_js
from socket import socket, AF_INET, SOCK_STREAM


class DirectoryServer(metaclass=Singleton):
    def __init__(self):
        self.__ds_socket = socket(AF_INET, SOCK_STREAM)
        self.__ds_socket.bind(load_js.load_config())
        print("Directory Server Address is at "
              "IP: " + self.__ds_socket.getsockname()[0] +
              ", PORT: " + str(self.__ds_socket.getsockname()[1]))
        self.__node_list = []  # addresses of all nodes in the toralina network

    def get_ds_socket(self):
        return self.__ds_socket

    def get_node_list(self):
        return self.__node_list

    def append_node_list(self, node_details):
        self.__node_list.append(node_details[1])
        print("appended node")
        print(self.__node_list)

    def remove_from_node_list(self, node_details):
        if node_details[1] in self.__node_list:
            self.__node_list.remove(node_details[1])
        print("removed node")
        print(self.__node_list)

    def __del__(self):
        self.__ds_socket.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__ds_socket.close()
