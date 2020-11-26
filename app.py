import os
import mysql.connector
import jwt
from server_to_app import Interface, redirect, render_html, error, return_auth_token
from models import User

app = Interface()

app_secret = '^gr05fr78^&tr3vr'

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

sql_database = mysql.connector.connect(
    host = DB_HOST,
    user = DB_USER,
    password = DB_PASS,
    database = "MiniClassroom"
)

def hello():
    return render_html("index.html")
app.route("/", hello)


def signup():
    if app.method == "GET":
        return render_html("signup.html")
    elif app.method == "POST":
        form_data = app.form_data
        name, email, passwd  = form_data["name"], form_data["email"], form_data["pwd"]
        new_user = User(emailID=email, password=passwd, name=name)
        if_inserted = new_user.add_user(sql_database)
        if(if_inserted == 0):
            return error(200, "The User Already exists. Please try another Email ID.")        
        return render_html("index.html")
app.route("/signup", signup)

def login():
    if app.method == "POST":
        form_data = app.form_data
        name, passwd  = form_data["name"], form_data["pwd"]
        user = User(password = passwd, name = name)
        if_logged_in = user.login_user(sql_database)
        if(if_logged_in == 0):
            return error(200, "Either the user does not exist or the given password is wrong. Please Try again")
        jwt_token = jwt.encode({'name': name}, app_secret, algorithm='HS256')
        return return_auth_token(jwt_token.decode("utf-8"))
    else:
        return error(405)
app.route("/login", login)