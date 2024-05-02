from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebEngineCore import *
from client import Client
from nodes.src.construct_messages import *


class ToralinaEngineView(QWebEngineView):
    def __init__(self, client: Client):
        super().__init__()
        self.__circuit = client.get_circuit()
        self.__circuit_id = client.get_circuit_id()

    # def triggerPageAction(self, action, checked=...):
    #     pass

    def load(self, url: QUrl):
        print("hi")
        super().load(url)

    def load(self, http_request: QWebEngineHttpRequest):
        # url = http_request.url()
        # header_names = list(http_request.headers())
        # header_values = list(map(lambda header_name: http_request.header(header_name), header_names))
        # post_data = http_request.postData()
        #
        # msg_data = get_network_msg_data(url, header_names, header_values, post_data)
        # network_msg = get_network_msg()
        #
        # print(header_values)
        print("hellooo")
        super().load(http_request)


class ToralinaInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self):
        super().__init__()

    def interceptRequest(self, info):
        info.block(True)


class ClientView(QWidget):
    def __init__(self, client: Client):
        super().__init__()

        self.__layout = QVBoxLayout()
        self.__website_view = ToralinaEngineView(client)

        self.__web_profile = QWebEngineProfile(self.__website_view)
        self.__web_profile.setRequestInterceptor(ToralinaInterceptor())

        self.__webpage = QWebEnginePage(self.__web_profile, self.__website_view)
        self.__website_view.setPage(self.__webpage)

        self.__layout.addWidget(self.__website_view)

        self.setLayout(self.__layout)

    def show_view(self):
        self.show()

    def load_url(self, url: str):
        self.__website_view.load(QUrl(url))

    def load_html(self, html_content: str):
        self.__website_view.setHtml(html_content)


def load_view(cv: ClientView, app: QApplication):
    cv.load_url("https://www.google.com")
    cv.show_view()
    app.exec()
