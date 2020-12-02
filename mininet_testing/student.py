import api
import sys


ip = sys.argv[1]
student_no = sys.argv[2]

app_api = api.API(ip, 12345)

app_api.post_signup_credentials(name="s{}".format(student_no), email="s{}@email.com".format(student_no), pwd="password")
app_api.post_login_credentials(email="s{}@email.com".format(student_no), pwd="password")