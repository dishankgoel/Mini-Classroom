import socket
from threading import Thread
from http_lib import HttpParser

class RequestThread(Thread):

    def __init__(self, sock, addr, buffer_size):

        Thread.__init__(self)
        self.addr = addr
        self.sock = sock
        self.buffer_size = buffer_size
        print("[+] New Connection from: ", addr)

    def run(self):

        http_object = HttpParser(self.sock, self.buffer_size)
        http_object.parse()
        # print("Request method: ", http_object.get_method())
        # print("Request uri: ", http_object.get_uri())
        # print("Request version: ", http_object.get_version())
        # print("Headers: ", http_object.get_headers())
        # print("Body: ", http_object.get_body())


ip = '127.0.0.1'
port = 12345

buffer_size = 2048

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:

    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_sock.bind((ip, port))
    print("Server Started on Port: ", port)
    while True:

        server_sock.listen(5)
        conn, addr = server_sock.accept()
        new_request = RequestThread(conn, addr, buffer_size)
        new_request.start()

