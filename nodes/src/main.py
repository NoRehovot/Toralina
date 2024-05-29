from PyQt6.QtWidgets import QApplication
from client.client import Client
from nodes.src.construct_messages import *
from client.client_protocol import initiate_client, listen_for_files
from node.dir_communication import update_client_list
from toralina_common.load_json import load_config
from view import ClientView
from threading import Thread

BUFF = 1024
DATA = ""
URL = ""


def main():
    app = QApplication(sys.argv)

    name = input("Enter Your Name: ")

    client = Client()
    cv = ClientView(client, name)

    ds_addr = load_config()
    client_socket = client.get_client_socket()

    while " " in name:
        name = input("No Spaces! Enter Your Name: ")

    update_client_list(client_socket, name, ds_addr)

    while not client.get_circuit():
        initiate_client(client)

    file_thread = Thread(target=listen_for_files, args=(client, cv), daemon=True)
    file_thread.start()

    cv.show_view()

    app.exec()


if __name__ == "__main__":
    main()
