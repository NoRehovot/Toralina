from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebEngineCore import *


class ToralinaEngineView(QWebEngineView):
    def __init__(self):
        super().__init__()

    def triggerPageAction(self, action, checked=...):
        pass

    def load(self, url: QUrl):
        pass

    def load(self, http_request: QWebEngineHttpRequest):
        pass


class ClientView(QWidget):
    def __init__(self):
        super().__init__()

        # define layout
        self.__layout = QVBoxLayout()
        self.__website_view = QWebEngineView()
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
