from client_protocol import *
from client import Client
from client_view import ClientView, load_view
from PyQt5.QtWidgets import QApplication


def main():
    client = Client()
    app = QApplication([])

    while not client.get_circuit():
        initiate_client(client)

    cv = ClientView()

    load_view(cv, app, client)


if __name__ == "__main__":
    main()
