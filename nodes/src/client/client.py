from nodes.src.node.node import Node
from toralina_common.singleton import Singleton


class Client(metaclass=Singleton):
    def __init__(self):
        self.__node = Node()
