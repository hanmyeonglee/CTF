import socket, select
from tls import TLSClientSession


def main():

    quit = False
    sock = None

    def callback(data):
        nonlocal quit, sock
        print(data)
        if data == b"bye\n":
            quit = True

    host, port = '141.223.175.203', 1337

    psk = bytes.fromhex(
        "b2c9b9f57ef2fbbba8b624070b301d7f278f1b39c352d5fa849f85a3e7a3f77b"
    )
    # session = TLSClientSession(
    #     server_names="127.0.0.1", psk=psk, data_callback=callback, psk_only=True, early_data=b"hoho"
    # )
    session = TLSClientSession(server_names=[host], data_callback=callback)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    sock.send(b'\x01', socket.MSG_OOB)
    sock.sendall(session.pack_client_hello())

    parser = session.parser()
    sock.setblocking(0)

    ready = select.select([sock], [], [], 2)
    if ready[0]:
        data = sock.recv(8192)

    parser.send(data)
    sock.sendall(parser.read())

    sock.sendall(session.pack_close())
    sock.close()


main()
