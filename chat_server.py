import socket
import mysql.connector
import concurrent.futures
from threading import *
import queue
import os
from models import *
import json

DB_HOST = os.getenv("DB_HOST") 
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")


sql_database = mysql.connector.connect(
    host = DB_HOST,
    user = DB_USER,
    password = DB_PASS,
    database = "MiniClassroom"
)


def get_json(sock):
    # size = int(sock.recv(buffer_size).decode("utf-8"))
    data = sock.recv(buffer_size).split(b"\r\n")
    size = int(data[0].decode("utf-8"))
    json_str = b""
    for i in range(1, len(data)):
        json_str += data[i]
    while len(json_str) != size:
        json_str += sock.recv(buffer_size).strip()
    json_str = json_str.decode("utf-8")
    json_str.strip()
    return json.loads(json_str)

def send_json(d, sock):
    data = json.dumps(d)
    size = len(bytes(data, "utf-8"))
    sock.sendall(bytes(str(size), "utf-8") + b"\r\n")
    sock.sendall(bytes(data, "utf-8") + b"\r\n")


def remove_connection(connection):

    if connection in active_clients:
        active_clients.remove(connection)

def broadcast_message(new_message, connection):

    for client in active_clients:
        if client != connection:
            try:
                send_json(new_message, client)
            except:
                client.close()
                remove_connection(client)
class RequestThread(Thread):

    def __init__(self, sock, addr, buffer_size):

        Thread.__init__(self)
        self.addr = addr
        self.sock = sock
        self.buffer_size = buffer_size
        print("[+] New Connection from: ", addr)

    def run(self):

        data = get_json(self.sock)            
        email, password = data["email"], data["password"]
        print(email)
        user = User(emailID=email, password=password)
        ret = user.login_user(sql_database)
        if(ret == 0):
            data = {"loggedIn": "0"}
            send_json(data, self.sock)
        else:
            user_id, name = ret[0], ret[1]
            data = {"loggedIn": "1", "name": name}
            send_json(data, self.sock)
            session_code = get_json(self.sock)["session_code"]
            user_attendance = Attendance(sessionID = session_code)
            ret = user_attendance.validate_sessionID(sql_database)
            if(ret == 0):
                send_json({"allowaccess": "0"}, self.sock)
            else:
                send_json({"allowaccess": "1"}, self.sock)
                while True:
                    try:
                        # new_message = self.sock.recv(self.buffer_size)
                        new_message = get_json(self.sock)
                        if new_message:
                            # name, content = new_message["name"], new_message["content"]
                            broadcast_message(new_message, self.sock)
                        else:
                            remove_connection(self.sock)
                    except:
                        continue

        self.sock.close()

ip = '127.0.0.1'
port = 12350

buffer_size = 2048

server_sock =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_sock.bind((ip, port))
server_sock.listen(100)
print("[*] Chat Server Started on Port: ", port)

active_clients = []

while True:
    conn, addr = server_sock.accept()
    active_clients.append(conn)
    new_request = RequestThread(conn, addr, buffer_size)
    new_request.start()

server_sock.close()