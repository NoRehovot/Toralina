from proxy import Proxy
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

from nodes.src.client.client import Client
from nodes.src.client.client_protocol import initiate_client


def main():
    client = Client()

    while not client.get_circuit():
        initiate_client(client)

    prox = Proxy(client)

    prox.listen_for_requests()


if __name__ == "__main__":
    main()