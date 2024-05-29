import os

from PyQt6.QtWidgets import QToolBar, QMainWindow, QTextEdit, QWidget, QListWidget, QGridLayout, QPushButton, QListWidgetItem, QLineEdit
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from client.client_protocol import *
from node.dir_communication import *
from toralina_common.load_json import load_config
import pathlib


class DroppableQTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, e: QDragEnterEvent):
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e: QDropEvent):
        if e.mimeData().hasUrls():
            url = e.mimeData().urls()[0]
            file_path = url.toLocalFile()
            self.setText(f"Dropped file: {file_path}")
            e.accept()
        else:
            e.ignore()


class ClientView(QMainWindow):
    def __init__(self, client: Client, name: str):
        super().__init__()
        self.__client = client
        self.__ds_addr = load_config()
        self.__client_name = name
        self.__client_to_messages = {}

        self.setFixedSize(1200, 800)
        self.setWindowTitle("Toralina - File Transfers With Onion Routing")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QGridLayout(central_widget)

        self.__chat_output = QListWidget()

        self.__chat_input = DroppableQTextEdit()
        self.__chat_input.setPlaceholderText("Drop files here...")

        self.__files_list = QListWidget()
        self.__files_list.clicked.connect(self.__open_file)

        self.__client_list = QListWidget()
        self.__client_list.clicked.connect(self.__update_message_view)

        self.__update_clients = QPushButton()
        self.__update_clients.setText("Update Client List")
        self.__update_clients.clicked.connect(self.__update_client_list)

        self.__toolbar = QToolBar()
        self.__toolbar.addWidget(self.__chat_input)
        self.__toolbar.addWidget(self.__files_list)

        layout.addWidget(self.__chat_output, 0, 0, 10, 7)
        layout.addWidget(self.__toolbar, 10, 0, 3, 10)
        layout.addWidget(self.__client_list, 0, 7, 9, 3)
        layout.addWidget(self.__update_clients, 9, 7, 1, 3)

        self.__chat_input.keyPressEvent = self.__handle_key_pressed

    def __is_message_file(self, msg):
        return "Dropped file: " in msg

    def __get_file_location(self, msg):
        return msg.split("file: ")[1]

    def __update_client_list(self):
        client_list = get_client_list(self.__client.get_client_socket(), self.__ds_addr)

        self.__client_list.clear()
        row = 0

        for client in client_list:
            if client != self.__client_name:
                self.__client_list.insertItem(row, QListWidgetItem(client))
                row += 1

    def __update_message_view(self):
        current_client_selection = self.__client_list.currentItem()

        if current_client_selection:
            self.__chat_output.clear()
            row = 0

            if current_client_selection.text() in self.__client_to_messages.keys():
                for message in self.__client_to_messages[current_client_selection.text()]:
                    self.__chat_output.insertItem(row, QListWidgetItem(message))
                    row += 1
        else:
            self.__chat_output.clear()

    def update_file_list(self):
        self.__files_list.clear()
        root = pathlib.Path(__file__).parent.resolve()
        path = f"{root}\\client\\client_files"

        print(path)

        filenames = os.listdir(path)
        print(filenames)
        row = 0

        for filename in filenames:
            print(filename)
            self.__files_list.insertItem(row, QListWidgetItem(filename))
            row += 1

    def update_client_messages(self, client_name: str, message: str):
        print(client_name, message)
        if client_name in self.__client_to_messages.keys():
            current_messages = self.__client_to_messages[client_name]
            current_messages.append(message)
        else:
            self.__client_to_messages[client_name] = [message]
        self.__update_message_view()

    def __handle_key_pressed(self, event):
        if event.key() == 16777220:
            print("ENTER")
            message = self.__chat_input.toPlainText().strip()
            if self.__is_message_file(message):
                file_location = self.__get_file_location(message)
                self.__send_file(file_location)

    def __send_file(self, file_location):
        if self.__client_list.currentItem():
            dest = self.__client_list.currentItem().text()
            send_file(file_location, dest, self.__client, self.__client_name)
            self.update_client_messages(dest, f"You: Sent a File ({file_location.split('/')[len(file_location.split('/'))-1]})")
            self.__chat_input.clear()
        else:
            return

    def __open_file(self):
        if self.__files_list.currentItem():
            root = pathlib.Path(__file__).parent.resolve()
            path = f"{root}\\client\\client_files"

            path = f"{path}\\{self.__files_list.currentItem().text()}"

            os.system(f'"{path}"')

    def show_view(self):
        self.show()
