import requests
import sys
import re

class API:

    def __init__(self, ip, port):

        self.ip = ip
        self.port = port
        self.session = requests.Session()
        self.cookie = {}
    
    def get_home_page(self):
        s = self.session
        r = s.get("http://{}:{}/".format(self.ip, self.port))
        return r.text
    
    def get_login_page(self):
        s = self.session
        r = s.get("http://{}:{}/login".format(self.ip, self.port))
        return r.text

    def post_login_credentials(self, email, pwd):
        s = self.session
        url = "http://{}:{}/login".format(self.ip, self.port)
        fields = {"email":email, "pwd":pwd}
        r = s.post(url, data=fields)
        self.cookie = s.cookies.get_dict()
        return r.text

    def get_signup_page(self):
        s = self.session
        r = s.get("http://{}:{}/signup".format(self.ip, self.port))
        return r.text

    def post_signup_credentials(self, name, email, pwd):
        s = self.session
        url = "http://{}:{}/signup".format(self.ip, self.port)
        fields = {"name":name, "email":email, "pwd":pwd}
        r = s.post(url, data=fields)
        self.cookie = s.cookies.get_dict()
        return r.text

    def post_join_classroom(self, code):
        s = self.session
        url = "http://{}:{}/JoinClass".format(self.ip, self.port)
        fields = {"code":code}
        r = s.post(url, data=fields)
        return r.text

    def post_create_classroom(self, name, description):
        s = self.session
        url = "http://{}:{}/CreateClass".format(self.ip, self.port)
        fields = {"name":name, "description":description}
        r = s.post(url, data=fields, cookies=self.cookie)
        html = r.text
        joining_code = re.search("Joining code:.*</p>", html).group(0).split()[-1].split('<')[0]
        return joining_code

    def get_classroom_view(self, classID):
        s = self.session
        r = s.get("http://{}:{}/classrooms/{}".format(self.ip, self.port, classID), cookies=self.cookie)
        return r.text

    def post_classroom_post(self, classID, content, tag):
        s = self.session
        url = "http://{}:{}/classrooms/{}".format(self.ip, self.port, classID)
        fields = {"content":content, "tag":tag}
        r = s.post(url, data=fields, cookies=self.cookie)
        return r.text

    def post_create_discussion(self, classID, gd_topic):
        s = self.session
        url = "http://{}:{}/classrooms/{}/group_discussions".format(self.ip, self.port, classID)
        fields = {"gd_topic":gd_topic}
        r = s.post(url, data=fields, cookies=self.cookie)
        return r.text

    def get_discussion_view(self, classID, discussionID):
        s = self.session
        r = s.get("http://{}:{}/classrooms/{}/group_discussions/{}".format(self.ip, self.port, classID, discussionID), cookies=self.cookie)
        return r.text

    def post_public_message(self, classID, discussionID, public_msg):
        s = self.session
        url = "http://{}:{}/classrooms/{}/group_discussions/{}".format(self.ip, self.port, classID, discussionID)
        fields = {"public_msg": public_msg, "if_private":0}
        r = s.post(url, data=fields, cookies=self.cookie)
        return r.text

    def post_private_message(self, classID, discussionID, private_msg, receiverID=-1):
        s = self.session
        url = "http://{}:{}/classrooms/{}/group_discussions/{}".format(self.ip, self.port, classID, discussionID)
        fields = {"private_msg": private_msg, "if_private":1}
        if receiverID!=-1:
            fields["receiver"] = receiverID
        r = s.post(url, data=fields, cookies=self.cookie)
        return r.text


# api = API('127.0.0.1', 12345)
# print(api.get_home_page())
# print(api.get_login_page())
# api.post_login_credentials(email="pushkarm27@gmail.com", pwd="password")
# print(api.get_classroom_view(1))
# print(api.post_public_message(1, 1, "Yo! ssup everyone?"))
# print(api.post_private_message(1, 1, "Hi harshit, this is from API", 2))
# print(api.post_create_classroom("API classroom", "this was made from API"))
# print(api.post_create_discussion(3, "API GD"))
# print(api.post_classroom_post(3, "API post number 2", "API_posts"))
