import socket
import sys
import getpass
import pickle

'''
Usage: python3 ./client.py <Server_IP> 
'''

ip = sys.argv[1]
port = 12350

buffer_size = 2048

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    s.connect((ip, port))
    email, password = "", ""
    email = input("Enter your Email ID: ")
    password = getpass.getpass("Enter your Password: ")
    data = {"email": email, "password": password}
    s.send(str(data))