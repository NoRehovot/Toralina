from node.exit_node_protocol import make_request_to_end_point
from nodes.src.client.client_view import load_view


def main():
    app, client_view = load_view()
    html_content = make_request_to_end_point("https://www.google.com")
    client_view.load_html(html_content.decode('utf-8'))
    client_view.show_view()
    app.exec()


if __name__ == "__main__":
    main()
