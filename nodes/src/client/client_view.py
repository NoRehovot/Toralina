import os
import sys
from client import Client
from nodes.src.construct_messages import *


def sys_append_modules() -> None:
    """
    Appends all important modules into sys_path.
    :returns: None.
    """
    parent = '../../../...'
    module = os.path.abspath(os.path.join(os.path.dirname(__file__), parent))
    sys.path.append(module)


sys_append_modules()


from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineUrlRequestInterceptor


BUFF = 1024


class ToralinaInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, client: Client):
        super().__init__()
        self.__circuit = client.get_circuit()
        self.__keys = client.get_keys()
        self.__circuit_id = client.get_circuit_id()
        self.__client_socket = client.get_client_socket()
        self.__page: QWebEnginePage = QWebEnginePage()
        self.__browser = QWebEngineView()

    def set_web_objects(self, page, browser):
        self.__page = page
        self.__browser = browser

    def interceptRequest(self, info):
        print("intercepted")
        info.block(True)
        url = info.requestUrl()
        print(url.toString())
        # if url.toString() != "https://www.google.com/":
        #     return
        headers = info.httpHeaders()
        header_names = list(map(lambda name: str(name), headers.keys()))
        header_values = list(map(lambda value: str(value), headers.values()))
        post_data = info.requestBody().readAll()

        msg_data = get_network_msg_data(url.toString(), header_names, header_values, post_data.data().decode('utf-8'))
        network_msg = get_network_msg(self.__circuit_id, msg_data, self.__keys, "yes")

        network_msg_split = network_msg.split("#-#")
        len_of_prefix = len("".join(network_msg_split[:3])) + 9

        if len(network_msg_split[3]) > 1024 - len_of_prefix:
            while msg_data:
                network_msg = get_network_msg(self.__circuit_id, msg_data[:int(BUFF/16)], self.__keys, "yes")
                network_msg = network_msg + "PADDING" + "A" * (BUFF - len(network_msg) - 7)
                self.__client_socket.send(network_msg.encode('utf-8'))
                if len(msg_data) < BUFF/16:
                    break
                msg_data = msg_data[int(BUFF/16):]
            end_msg = get_end_network_msg(self.__circuit_id, self.__keys, "yes")
            self.__client_socket.send(end_msg.encode('utf-8'))
        else:
            self.__client_socket.send(network_msg.encode('utf-8'))
            end_msg = get_end_network_msg(self.__circuit_id, self.__keys, "yes")
            self.__client_socket.send(end_msg.encode('utf-8'))

        response = self.__client_socket.recv(BUFF)
        data = ""
        while response:
            html_data = response.decode('utf-8').split("#-#")[3].split("PADDING")[0]
            if html_data == " ":
                break
            html_data = decrypt_string(html_data.encode('utf-8'), self.__keys)
            data += html_data
            response = self.__client_socket.recv(BUFF)

        print(data.encode('utf-8'))

        self.__page.setHtml(data)
        self.__browser.setPage(self.__page)


class ToralinaWebPage(QWebEnginePage):
    def acceptNavigationRequest(self, url, _type, isMainFrame):
        print("acceptNavigationRequest")
        print(url)
        return QWebEnginePage.acceptNavigationRequest(self, url, _type, isMainFrame)


class ClientView(QWidget):
    def __init__(self):
        super().__init__()
        self.__layout = QVBoxLayout()
        self.setFixedSize(1500, 1000)

    def set_browser_layout(self, website_view):
        self.__layout.addWidget(website_view)

        self.setLayout(self.__layout)

    def show_view(self):
        self.show()


def load_view(cv: ClientView, app: QApplication, client: Client):
    browser = QWebEngineView()
    interceptor = ToralinaInterceptor(client)
    profile = QWebEngineProfile()
    profile.setUrlRequestInterceptor(interceptor)
    page = ToralinaWebPage(profile, browser)
    page.setUrl(QUrl("https://www.google.com"))
    interceptor.set_web_objects(page, browser)
    # browser.setPage(page)
    # browser.show()
    cv.set_browser_layout(browser)
    cv.show_view()
    app.exec()
