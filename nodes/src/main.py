from nodes.src.node.node import Node


def main():
    n = Node()
    n.get_node_list_from_ds()
    print("The Toralina node list:")
    print(n.get_this_node_list())


if __name__ == "__main__":
    main()
