from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebEngineCore import *
from client import Client


class ToralinaEngineView(QWebEngineView):
    def __init__(self, circuit: list):
        super().__init__()
        self.__circuit = circuit

    def triggerPageAction(self, action, checked=...):
        pass

    def load(self, url: QUrl):

        pass

    def load(self, http_request: QWebEngineHttpRequest):
        url = http_request.url()
        header_names = list(http_request.headers())
        header_values = list(map(lambda header_name: http_request.header(header_name), header_names))
        post_data = http_request.postData()

        print(header_values)


        pass


class ToralinaInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, parent):
        super().__init__(parent)

    def interceptRequest(self, info):
        pass


class ClientView(QWidget):
    def __init__(self, client: Client):
        super().__init__()

        # define layout
        self.__layout = QVBoxLayout()
        self.__website_view = ToralinaEngineView(client.get_circuit())
        self.__layout.addWidget(self.__website_view)

        # load layout
        self.setLayout(self.__layout)

    def show_view(self):
        self.show()

    def load_url(self, url: str):
        self.__website_view.load(QUrl(url))

    def load_html(self, html_content: str):
        self.__website_view.setHtml(html_content)


def load_view():
    app = QApplication([])
    client_view = ClientView()
    return app, client_view
