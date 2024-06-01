from toralina_common.ip_utils import get_free_port_socket
from nodes.src.construct_messages import get_file_msg, decrypt_string, encrypt_string
import time

BUFF = 1024


def send_file_msg(file_content, file_msg_data, keys, circuit_id, to, last_signal="yes"):
    s = get_free_port_socket()
    s.connect(to)

    print("starting file conversation")

    s.send(get_file_msg(circuit_id, file_msg_data, keys, last_signal).encode('utf-8'))
    s.recv(BUFF)

    print("got confirmation, sending file")

    encrypted_file_msg_data = encrypt_string(file_content, keys, False)

    while encrypted_file_msg_data:
        msg_data = encrypted_file_msg_data[:960]
        msg_data = msg_data + b"PADDING" + b"A" * (1024 - len(msg_data) - 7)

        s.send(msg_data)

        if len(encrypted_file_msg_data) < 960:
            break

        encrypted_file_msg_data = encrypted_file_msg_data[960:]

    s.send("4".encode('utf-8'))

    return s


def receive_file_msg(sock, keys):
    all_data = b""
    while True:
        msg = sock.recv(BUFF)
        print(msg)

        if msg == "4".encode('utf-8'):
            break

        msg = msg.split(b"PADDING")[0]

        all_data += msg

    all_data = decrypt_string(all_data, keys, False)

    return all_data
