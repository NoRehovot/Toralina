import os
import sys
from PyQt5.QtCore import QByteArray


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


def encrypt_string(this_str, keys, should_encode=True):
    if should_encode:
        this_str = this_str.encode('utf-8')
    for k in reversed(keys):
        f = Fernet(k)
        this_str = f.encrypt(this_str)
    return this_str


def decrypt_string(this_str, keys, should_decode=True):
    for k in keys:
        f = Fernet(k)
        this_str = f.decrypt(this_str)
    if should_decode:
        this_str = this_str.decode('utf-8')
    return this_str


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


def get_file_msg_data(filename: str, dest: str, src: str):
    return f"{filename}:--:{dest}:--:{src}"


def unpack_msg_data(data: str):
    data = data.split(":--:")

    return data[0], data[1], data[2]


def get_file_msg(circuit_id, data, keys, last_signal):
    msg = "#-#".join([circuit_id, "3", encrypt_string(last_signal, keys).decode('utf-8'),
                      encrypt_string(data, keys).decode('utf-8')])
    return msg


def get_normal_msg_data(data: str, dest: str, src: str):
    return f"{data}:--:{dest}:-:{src}"


def get_normal_msg(circuit_id, data, keys, last_signal):
    msg = "#-#".join([circuit_id, "4", encrypt_string(last_signal, keys).decode('utf-8'),
                      encrypt_string(data, keys).decode('utf-8')])
    return msg