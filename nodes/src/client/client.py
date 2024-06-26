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
        self.__circuit = []
        self.__circuit_id = None
        self.__keys = []

    def get_node(self) -> Node:
        return self.__node

    def get_client_socket(self):
        return self.__client_socket

    def set_circuit(self, circuit: list):
        self.__circuit = circuit

    def get_circuit(self) -> list:
        return self.__circuit

    def set_circuit_id(self, circuit_id: str):
        self.__circuit_id = circuit_id

    def get_circuit_id(self) -> str:
        return self.__circuit_id

    def set_keys(self, keys):
        self.__keys = keys

    def get_keys(self):
        return self.__keys

    def __del__(self):
        self.__client_socket.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__client_socket.close()
