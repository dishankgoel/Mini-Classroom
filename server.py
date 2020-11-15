import socket
from threading import Thread

class RequestThread(Thread):

    def __init__(self, sock, addr):

        Thread.__init__(self)
        self.addr = addr
        self.sock = sock
        print("[+] New Connection from: ", addr)

    def run(self):

        pass


ip = '127.0.0.1'
port = 12345

buffer_size = 1024

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:

    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_sock.bind((ip, port))

    while True:

        server_sock.listen(5)
        conn, addr = server_sock.accept()
        new_request = RequestThread(conn, addr)
        new_request.start()

