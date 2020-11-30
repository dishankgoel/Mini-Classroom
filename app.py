import os
import mysql.connector
import jwt
from server_to_app import Interface, redirect, render_html, error
from models import *

app = Interface()

app_secret = '^gr05fr78^&tr3vr'

DB_HOST = "localhost"
DB_USER = "root"
DB_PASS = "root"

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
        user_id = new_user.add_user(sql_database)
        if(user_id == -1):
            return error(200, "The User Already exists. Please try another Email ID.")        
        jwt_token = jwt.encode({'emailID': email, 'userID': user_id, 'name': name}, app_secret, algorithm='HS256')
        return redirect(new_route="/classrooms", token=jwt_token.decode("utf-8"))
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
    ret_code, user = validate_login(app.headers)
    if(ret_code == 0):
        return user
    else:
        joined_classes = user.list_classrooms(sql_database)
        classroom_data = []
        for joined_class in joined_classes:
            classroom_data.append({"name": joined_class.name, "description": joined_class.description, "classid": joined_class.classID, "code": joined_class.joining_code, "userid": user.userID, "creatorid": joined_class.creator_userID})
        return render_html("classrooms.html", classrooms = classroom_data)
app.route("/classrooms", classrooms)


def access_classroom(class_id):
    ret_code, user = validate_login(app.headers)
    if(ret_code == 0):
        return user
    else:
        joined_classes = user.list_classrooms(sql_database)
        class_ids = [joined_class.classID for joined_class in joined_classes]
        if class_id not in class_ids:
            return error(200, "You are not a part of this classroom")
        classroom_obj = Classroom(classID=class_id)
        for joined_class in joined_classes:
            if joined_class.classID == class_id:
                classroom_obj = joined_class
                break

        if app.method == "POST":
            if(user.userID == classroom_obj.creator_userID):
                form_data = app.form_data
                content = form_data["content"]
                tag = form_data["tag"]
                post = Post(classID=classroom_obj.classID, creator_userID=user.userID, content=content)
                post.add_post(sql_database)
                new_tag = Tag(tagName=tag, postID=post.postID, classID=classroom_obj.classID)
                new_tag.add_tag(sql_database)
                return redirect("/classrooms/{}".format(class_id))
            else:
                return error(200, "You are not a Instructor. Only instructors can post on Classroom")
        else:
            posts = classroom_obj.list_posts(sql_database=sql_database)
            user_details = {}
            user_details["username"] = user.name
            user_details["userID"] = user.userID
            classroom_details = {"classID": classroom_obj.classID}
            classroom_details["creator_name"] = classroom_obj.get_creator_name(sql_database=sql_database)[0][0]
            classroom_details["creator_userID"] = classroom_obj.creator_userID
            classroom_details["name"] = classroom_obj.name
            classroom_details["description"] = classroom_obj.description
            post_list = []
            for post in posts:
                tag_name = post.get_tag(sql_database)
                post_list.append({"postID":post.postID, "classID":post.classID, "timestamp":post.timestamp, "creator_userID":post.creator_userID, "content":post.content, "tag":tag_name})
            
            if_class_live = LiveClass(classID=classroom_obj.classID).check_if_live(sql_database)
            return render_html("class.html", posts=post_list, details=classroom_details, user_details = user_details, if_class_live = if_class_live)
app.route("access_classroom", access_classroom)

def create_classroom():
    if app.method == "GET":
        return render_html("create_class.html")
    ret_code, user = validate_login(app.headers)
    if(ret_code == 0):
        return user
    else:
        form_data = app.form_data
        name, description = form_data['name'], form_data['description']
        new_class = Classroom(creator_userID=user.userID, name=name, description=description)
        new_class.add_class(sql_database)
        new_classroom_user_role = Classroom_user_role(classID=new_class.classID, userID=user.userID, role=0)
        new_classroom_user_role.add_role(sql_database)
        return redirect("/classrooms")
app.route("/CreateClass", create_classroom)

def join_classroom():
    if app.method == "GET":
        return render_html("join_class.html")
    ret_code, user = validate_login(app.headers)
    if(ret_code == 0):
        return user
    else:
        joining_code = app.form_data['code']
        find_class = Classroom(joining_code=joining_code)
        classID = find_class.get_id_from_code(sql_database)
        user_role = Classroom_user_role(classID=classID, userID=user.userID, role=1)
        user_role.add_role(sql_database)
        return redirect("/classrooms")
app.route("/JoinClass", join_classroom)

def start_classroom_session():
    ret_code, user = validate_login(app.headers)
    if(ret_code == 0):
        return user
    else:
        if(app.method == "POST"):
            classID = app.form_data["classID"]
            live_class = LiveClass(classID=classID)
            status = live_class.start(sql_database)
            if(status == 0):
                return error(200, "The Class has already been started, please join the class at: /classrooms/{}/live".format(classID))
            else:
                return redirect("/classrooms/{}/live".format(classID))
        else:
            return error(405)
app.route("/start_class", start_classroom_session)


def join_live_class(classID):
    ret_code, user = validate_login(app.headers)
    if(ret_code == 0):
        return user
    else:
        live_class = LiveClass(classID=classID)
        if_live = live_class.check_if_live(sql_database)
        if not if_live:
            return error(400, "The class has not started yet.")
        if app.method == "GET":
            live_messages = LiveMessages(liveclassID=live_class.liveclassID)
            live_messages.get_all_messages(sql_database)
            classroom_details = Classroom(classID=classID).get_class_details(sql_database)
            return render_html("live_class.html", messages = live_messages.all_messages, classroom_details = classroom_details)
        elif app.method == "POST":
            message = app.form_data["message"]
            live_message = LiveMessages(liveclassID=live_class.liveclassID, userID=user.userID, content=message)
            live_message.send_message(sql_database)
            return redirect("/classrooms/{}/live".format(live_class.liveclassID))
        else:
            return error(405)
app.route("join_live_class", join_live_class)