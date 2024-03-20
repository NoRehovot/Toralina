import os
import sys


def sys_append_modules() -> None:
    """
    Appends all important modules into sys_path.
    :returns: None.
    """
    parent = '../../...'
    module = os.path.abspath(os.path.join(os.path.dirname(__file__), parent))
    sys.path.append(module)


sys_append_modules()

from cryptography.fernet import Fernet


def encrypt_string(this_str, keys):
    this_str = this_str.encode('utf-8')
    for k in reversed(keys):
        f = Fernet(k)
        this_str = f.encrypt(this_str)
    return this_str


def decrypt_string(this_str, keys):
    for k in keys:
        f = Fernet(k)
        this_str = f.decrypt(this_str)
    return this_str.decode('utf-8')


def get_add_node_data(node_details):
    return node_details[0] + " " + str(node_details[1])


def get_add_node_msg(circuit_id, data, keys, last_signal):
    msg = "#-#".join([circuit_id, "1", encrypt_string(last_signal, keys).decode('utf-8'), encrypt_string(data, keys).decode('utf-8')])
    return msg


def get_confirm_msg(circuit_id, data, keys):
    msg = "#-#".join([circuit_id, "0", "-", encrypt_string(data, keys).decode('utf-8')])
    return msg


def get_send_key_msg(circuit_id, data, keys, last_signal):
    msg = "#-#".join([circuit_id, "2", encrypt_string(last_signal, keys).decode('utf-8'), encrypt_string(data, keys).decode('utf-8')])
    return msg


def get_network_msg_data(url: str, headers, post_data):
    return f"{url}"


def get_network_msg(circuit_id, data, keys, last_signal):
    pass
