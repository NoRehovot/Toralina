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

import toralina_common.ip_utils as ipu
import nodes.src.node.dir_communication as dircom
from toralina_common.singleton import Singleton


class Node(metaclass=Singleton):
    def __init__(self):
        self.__node_socket = ipu.get_free_port_socket()
        self.__node_list = []
        self.__is_midpoint = bool()
        self.__is_exit_node = bool()
        self.start_node()
        self.__get_node_list_from_ds()

    def get_node_socket(self):
        return self.__node_socket

    def start_node(self):
        dircom.update_node_list(self, 1)
        self.turn_midpoint_on()

    def stop_node(self):
        dircom.update_node_list(self, 2)
        self.turn_midpoint_off()

    def __get_node_list_from_ds(self):
        self.__node_list = dircom.get_node_list(self)

    def get_this_node_list(self):
        self.__get_node_list_from_ds()
        return self.__node_list

    def turn_midpoint_on(self):
        self.__is_midpoint = True

    def turn_midpoint_off(self):
        self.__is_midpoint = False

    def is_midpoint(self):
        return self.__is_midpoint

    def __del__(self):
        self.stop_node()
        self.__node_socket.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_node()
        self.__node_socket.close()
