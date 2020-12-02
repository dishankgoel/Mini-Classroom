import socket
import mysql.connector
import concurrent.futures
from threading import *
import queue
import os, sys
from models import *
import json


'''
Usage: python3 ./chat_server.py <ip>
'''


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
    try:
        size = int(data[0].decode("utf-8"))
    except:
        print("[*] Connection Ended")
        sys.exit(0)
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


def validate_classroom(classID, user):

    joined_classes = user.list_classrooms(sql_database)
    class_ids = [joined_class.classID for joined_class in joined_classes]
    if classID not in class_ids:
        return 0, "You are not a part of this classroom"
    classroom_obj = Classroom(classID=classID)
    for joined_class in joined_classes:
        if joined_class.classID == classID:
            classroom_obj = joined_class
            break
    return 1, classroom_obj


def remove_live_connection(connection, liveclassID):

    if liveclassID in active_classrooms:
        if connection in active_classrooms[liveclassID]:
            active_classrooms[liveclassID].remove(connection)

def add_live_connection(connection, liveclassID):
    if liveclassID not in active_classrooms:
        active_classrooms[liveclassID] = [connection,]
    else:
        active_classrooms[liveclassID].append(connection)

def broadcast_live_message(new_message, connection, liveclassID):

    for client in active_classrooms[liveclassID]:
        if client != connection:
            try:
                send_json(new_message, client)
            except:
                client.close()
                remove_live_connection(client, liveclassID)

def remove_group_connection(connection, classID):

    if classID in group_chats:
        if connection in group_chats[classID]:
            group_chats[classID].remove(connection)

def add_group_connection(connection, classID):
    if classID not in group_chats:
        group_chats[classID] = [connection,]
    else:
        group_chats[classID].append(connection)

def broadcast_group_message(new_message, connection, classID):

    for client in group_chats[classID]:
        if client != connection:
            try:
                send_json(new_message, client)
            except:
                client.close()
                remove_group_connection(client, classID)

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
            choice = get_json(self.sock)
            if choice["live"] == "1":
                user_attendance = Attendance(sessionID = choice["session_code"], userID=user_id)
                ret = user_attendance.validate_sessionID(sql_database)
                if(ret == 0):
                    send_json({"allowaccess": "0"}, self.sock)
                else:
                    send_json({"allowaccess": "1"}, self.sock)
                    add_live_connection(self.sock, user_attendance.liveclassID)
                    while True:
                        try:
                            new_message = get_json(self.sock)
                            if new_message:
                                broadcast_live_message(new_message, self.sock, user_attendance.liveclassID)
                            else:
                                remove_live_connection(self.sock, user_attendance.liveclassID)
                        except:
                            break
            else:
                classID = Classroom(joining_code = choice["joining_code"]).get_id_from_code(sql_database)
                ret = validate_classroom(classID, User(userID=user_id))
                if(ret[0] == 0):
                    send_json({"allowaccess": "0"}, self.sock)
                else:
                    send_json({"allowaccess": "1"}, self.sock)
                    add_group_connection(self.sock, classID)
                    while True:
                        try:
                            new_message = get_json(self.sock)
                            if new_message:
                                broadcast_group_message(new_message, self.sock, classID)
                            else:
                                remove_group_connection(self.sock, classID)
                        except:
                            break

        self.sock.close()

ip = sys.argv[1]
port = 12350

buffer_size = 2048

server_sock =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_sock.bind((ip, port))
server_sock.listen(100)
print("[*] Chat Server Started on Port: ", port)

active_classrooms = {}
group_chats = {}

while True:
    conn, addr = server_sock.accept()
    new_request = RequestThread(conn, addr, buffer_size)
    new_request.start()

server_sock.close()