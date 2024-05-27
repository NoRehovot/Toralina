from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QKeySequence, QAction
from PyQt6.QtWidgets import QApplication, QLineEdit, QToolBar, QMainWindow
from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEnginePage, QWebEngineProfile, QWebEngineScript
from PyQt6.QtWebEngineWidgets import QWebEngineView
from client.client import Client
from nodes.src.construct_messages import *
from client.client_protocol import initiate_client
from nodes.src.proxy.set_proxy import set_proxy

BUFF = 1024
DATA = ""
URL = ""


class MyWebEnginePage(QWebEnginePage):
    def acceptNavigationRequest(self, url, _type, isMainFrame):
        print("acceptNavigationRequest")
        return QWebEnginePage.acceptNavigationRequest(self, url, _type, isMainFrame)


def save_data_to_html_file(data: str):
    with open("browser_display.html", 'w', encoding='utf-8') as f:
        print(data)
        f.write(data)


class ToralinaInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self):
        super().__init__()
        # self.__circuit = client.get_circuit()
        # self.__keys = client.get_keys()
        # self.__circuit_id = client.get_circuit_id()
        # self.__client_socket = client.get_client_socket()
        # self.__page: QWebEnginePage = QWebEnginePage()
        # self.__browser = QWebEngineView()

    # def set_web_objects(self, browser):
    #     self.__browser = browser
    #
    # def __handle_response_data(self, full_data, url):
    #     if "<!DOCTYPE html>" in full_data or "<!doctype html>" in full_data:
    #         print("HTML")
    #         self.__browser.page().setHtml(full_data)
    #     elif "function" in full_data:
    #         print("CODE")
    #         script = QWebEngineScript()
    #         script.setSourceCode(full_data)
    #         script.setSourceUrl(QUrl(url))
    #         print(self.__browser.page().scripts().toList())
    #         self.__browser.page().scripts().insert(script)
    #     elif full_data:
    #         print("IMAGE")
    #         if full_data[:2] == "b'":
    #             full_data = full_data[2:len(full_data) - 1]
    #
    #         image_type = url.split(".")[len(url.split(".")) - 1]
    #
    #         js_script = f"var binaryData = '" + full_data + "';" + \
    #                     "var img = document.createElement('img');" + \
    #                     f"img.src = 'data:image/{image_type};base64,' + binaryData;" + \
    #                     "document.body.appendChild(img);"
    #
    #         script = QWebEngineScript()
    #         script.setSourceCode(js_script)
    #         script.setSourceUrl(QUrl(url))
    #         self.__browser.page().scripts().insert(script)

    def interceptRequest(self, info):

        info.setHttpHeader(b"is_toralina", b"yes")

        print("\nintercepted")


class ClientView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1200, 800)
        self.__search_bar = QLineEdit()
        self.__website_view = QWebEngineView()

    def set_browser_layout(self, website_view):
        self.__website_view = website_view

        toolbar = QToolBar()

        # Add a back action to the toolbar
        back_action = QAction("Back", self)
        back_action.setShortcut(QKeySequence("Back"))
        back_action.triggered.connect(self.__website_view.back)
        toolbar.addAction(back_action)

        # Add a forward action to the toolbar
        forward_action = QAction("Forward", self)
        forward_action.setShortcut(QKeySequence("Forward"))
        forward_action.triggered.connect(self.__website_view .forward)
        toolbar.addAction(forward_action)

        # Add a reload action to the toolbar
        reload_action = QAction("Reload", self)
        reload_action.setShortcut(QKeySequence("Refresh"))
        reload_action.triggered.connect(self.__website_view .reload)
        toolbar.addAction(reload_action)

        go_home_action = QAction("Home", self)
        go_home_action.triggered.connect(self.navigate_home)
        toolbar.addAction(go_home_action)

        self.__website_view.loadFinished.connect(self.__update_title)
        self.__website_view.urlChanged.connect(self.__update_search_bar)

        self.__search_bar.returnPressed.connect(self.__load_url)
        toolbar.addWidget(self.__search_bar)

        self.addToolBar(toolbar)
        self.setCentralWidget(self.__website_view)

    def __load_url(self):
        url = self.__search_bar.text()

        if "http" not in url:
            print(url)
            url = "https://" + url
            print(url)
        self.__website_view.page().setUrl(QUrl(url))

    def __update_title(self):
        print("updating title")
        title = self.__website_view.page().title()
        self.setWindowTitle("% s - Toralina" % title)

    def __update_search_bar(self, url):
        print("updating searchbar")

        if url.toString()[:9] != "data:text":
            self.__search_bar.setText(url.toString())

            self.__search_bar.setCursorPosition(0)

    def navigate_home(self):
        self.__website_view.page().setUrl(QUrl("http://www.google.com"))

    def show_view(self):
        self.show()


def main():
    app = QApplication(sys.argv)
    set_proxy()

    cv = ClientView()
    browser = QWebEngineView()
    cv.set_browser_layout(browser)
    profile = QWebEngineProfile()
    interceptor = ToralinaInterceptor()
    profile.setUrlRequestInterceptor(interceptor)
    page = MyWebEnginePage(profile, browser)
    browser.setPage(page)

    # interceptor.set_web_objects(browser)

    cv.navigate_home()

    cv.show_view()

    app.exec()


if __name__ == "__main__":
    main()
