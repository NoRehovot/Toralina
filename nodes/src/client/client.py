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
from toralina_common.singleton import Singleton
import toralina_common.ip_utils as ipu


class Client(metaclass=Singleton):
    def __init__(self):
        self.__node = Node()
        self.__node.stop_node()
        self.__client_socket = ipu.get_free_port_socket()

    def get_node(self):
        return self.__node

    def get_client_socket(self):
        return self.__client_socket

    def __del__(self):
        self.__client_socket.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__client_socket.close()
