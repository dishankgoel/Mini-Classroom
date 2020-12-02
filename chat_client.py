import socket
import sys
import getpass
import json
import select

'''
Usage: python3 ./client.py <Server_IP> 
'''
try:
    ip = sys.argv[1]
except:
    ip = '127.0.0.1'
port = 12350

buffer_size = 2048

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

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    s.connect((ip, port))
    email, password = "", ""
    email = input("Enter your Email ID: ")
    password = getpass.getpass("Enter your Password: ")
    data = {"email": email, "password": password}
    send_json(data, s)
    ret = get_json(s)
    if(ret["loggedIn"] == "0"):
        print("Either User does not exist or password is incorrect")
    else:
        name = ret["name"]
        print("Welcome {}!".format(name))
        print("1. Join live class")
        print("2. Group Chat")
        choice = input("Choice: ")
        if int(choice) == 1:
            session_code = input("Enter your Session Code for live Class: ")
            send_json({"live": "1", "session_code": session_code}, s)
            response = get_json(s)
            if(response["allowaccess"] == "0"):
                print("Either the given session code is wrong or class has not started yet")
            else:
                print("You have entered the live classroom!")
                while True:
                    sockets_list = [sys.stdin, s]
                    print("{}: ".format(name), end="", flush=True)
                    read_sockets,write_socket, error_socket = select.select(sockets_list, [], [])
                    for sock in read_sockets:
                        if sock == s:
                            data = get_json(sock)
                            print("\n{}: {}".format(data["name"], data["content"]), flush=True)
                        else:
                            message = input()
                            send_json({"name": name, "content": message}, s)
        elif int(choice) == 2:
            joining_code = input("Enter joining code for your classroom: ")
            send_json({"live": 0, "joining_code": joining_code}, s)
            response = get_json(s)
            if(response["allowaccess"] == "0"):
                print("You are not part of this classroom")
            else:
                print("You have entered the group chat!")
                while True:
                    sockets_list = [sys.stdin, s]
                    print("{}: ".format(name), end="", flush=True)
                    read_sockets,write_socket, error_socket = select.select(sockets_list, [], [])
                    for sock in read_sockets:
                        if sock == s:
                            data = get_json(sock)
                            print("\n{}: {}".format(data["name"], data["content"]), flush=True)
                        else:
                            message = input()
                            send_json({"name": name, "content": message}, s)
        else:
            print("Invalid choice")
                            
