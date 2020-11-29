import os
import mysql.connector
import jwt
from server_to_app import Interface, redirect, render_html, error
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

def validate_login(headers):
    if 'Cookie' not in headers:
        return 0, error(401, "You have to be logged in to see this page")
    else:
        token = headers['Cookie'].split("=")[-1]
        try:
            decoded = jwt.decode(token, app_secret, algorithms='HS256')
            new_user = User(userID=decoded["userID"], emailID=decoded["emailID"], name=decoded["name"])
            return 1, new_user
        except:
            return 0, error(200, "Either the user does not exist or the given password is wrong. Please Try again")

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
        email, passwd  = form_data["email"], form_data["pwd"]
        user = User(password = passwd, emailID=email)
        ret = user.login_user(sql_database)
        if(ret == 0):
            return error(200, "Either the user does not exist or the given password is wrong. Please Try again")
        user_id = ret[0]
        name = ret[1]
        jwt_token = jwt.encode({'emailID': email, 'userID': user_id, 'name': name}, app_secret, algorithm='HS256')
        return redirect(new_route="/classrooms", token=jwt_token.decode("utf-8"))
    else:
        return render_html("login.html")
app.route("/login", login)

def classrooms():
    code, user = validate_login(app.headers)
    if(code == 0):
        return user
    else:
        joined_classes = user.list_classrooms(sql_database)
        classroom_data = []
        for joined_class in joined_classes:
            classroom_data.append({"name": joined_class.name, "description": joined_class.description, "link": "/classrooms/{}".format(joined_class.classID)})
        return render_html("classrooms.html", classrooms = classroom_data)
app.route("/classrooms", classrooms)


def access_classroom(class_id):
    code, user = validate_login(app.headers)
    if(code == 0):
        return user
    else:
        joined_classes = user.list_classrooms(sql_database)
        class_ids = [joined_class.classID for joined_class in joined_classes]
        if class_id not in class_ids:
            return error(200, "You are not a part of this classroom")
        return render_html("lol")
app.route("access_classroom", access_classroom)

def create_classroom():
    if app.method == "GET":
        return render_html("create_class.html")
    form_data = app.form_data

    pass

app.route("/CreateClass", create_classroom)

def join_classroom():
    if app.method == "GET":
        return render_html("join_class,html")
    form_data = app.form_data
    pass
app.route("/JoinClass", join_classroom)
