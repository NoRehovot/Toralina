import subprocess
from socket import *

BUFF = 1024


def get_this_ip():
    """
    Parameters: -
    Returns: ip (string)

    This function returns the computer's ip
    """
    output = str(subprocess.check_output("ipconfig"))
    output = output.replace(". ", "").replace(" ", "").replace(r"\r", "").replace(r"\n", ":").split(":")
    ip = output[output.index("IPv4Address") + 1]
    return ip


def get_free_port_socket():
    """
    Parameters: -
    Returns: socket object

    This function finds available port to use for communication
    """
    ip = get_this_ip()

    s = socket(AF_INET, SOCK_STREAM)
    s.bind((ip, 0))  # let the system find an open port
    return s


def send_message(msg, send_to):
    with get_free_port_socket() as s:
        s.connect(send_to)
        s.send(msg)
        response = s.recv(BUFF)

    return response.decode('utf-8')
