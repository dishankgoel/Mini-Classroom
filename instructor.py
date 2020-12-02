import api
import sys

ip = sys.argv[1]


app_api = api.API(ip, 12345)

app_api.post_signup_credentials(name="i1", email="i1@email.com", pwd="password")
app_api.post_login_credentials(email="i1@email.com", pwd="password")
print("[*] Joining code: {}".format(app_api.post_create_classroom(name="CN: CS 433", description="Computer Networks")))
