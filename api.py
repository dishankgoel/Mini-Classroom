import requests
import sys


class API:

    def __init__(self, ip, port):

        self.ip = ip
        self.port = port
    
    def get_home_page(self):

        r = requests.get("http://{}:{}/".format(self.ip, self.port))
        return r.text


api = API('127.0.0.1', 12345)
print(api.get_home_page())
