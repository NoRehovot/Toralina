from client_protocol import *
from client import Client
from client_view import ClientView


def main():
    client = Client()

    while not client.get_circuit():
        initiate_client(client)

    ClientView(client)


if __name__ == "__main__":
    main()
