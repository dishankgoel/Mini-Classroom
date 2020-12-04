import os
import mysql.connector
import jwt
from server_to_app import Interface, redirect, render_html, error
from models import *

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

def validate_classroom(classID, user):

    joined_classes = user.list_classrooms(sql_database)
    class_ids = [joined_class.classID for joined_class in joined_classes]
    if classID not in class_ids:
        return 0, error(200, "You are not a part of this classroom")
    classroom_obj = Classroom(classID=classID)
    for joined_class in joined_classes:
        if joined_class.classID == classID:
            classroom_obj = joined_class
            break
    return 1, classroom_obj

def user_json(user):
    user_details = {}
    user_details["username"] = user.name
    user_details["userID"] = user.userID
    return user_details

def classroom_json(classroom_obj):
    classroom_details = {"classID": classroom_obj.classID}
    classroom_details["creator_name"] = classroom_obj.get_creator_name(sql_database=sql_database)[0][0]
    classroom_details["creator_userID"] = classroom_obj.creator_userID
    classroom_details["name"] = classroom_obj.name
    classroom_details["description"] = classroom_obj.description
    return classroom_details


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

def logout():
    return redirect(new_route="/", token="", token_expires = True)
app.route("/logout", logout)

def classrooms():
    ret_code, user = validate_login(app.headers)
    if(ret_code == 0):
        return user
    else:
        joined_classes = user.list_classrooms(sql_database)
        user_details = user_json(user)
        classroom_data = []
        for joined_class in joined_classes:
            classroom_data.append({"name": joined_class.name, "description": joined_class.description, "classid": joined_class.classID, "code": joined_class.joining_code, "userid": user.userID, "creatorid": joined_class.creator_userID})
        return render_html("classrooms.html", classrooms = classroom_data, user_details = user_details)
app.route("/classrooms", classrooms)


def access_classroom(class_id):
    ret_code, user = validate_login(app.headers)
    if(ret_code == 0):
        return user
    else:
        ret_code, classroom_obj = validate_classroom(class_id, user)
        if(ret_code == 0):
            return classroom_obj
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
            user_details = user_json(user)
            classroom_details = classroom_json(classroom_obj)
            post_list = []
            for post in posts:
                tag_name = post.get_tag(sql_database)
                post_list.append({"postID":post.postID, "classID":post.classID, "timestamp":post.timestamp, "creator_userID":post.creator_userID, "content":post.content, "tag":tag_name})
            
            if_class_live = LiveClass(classID=classroom_obj.classID).check_if_live(sql_database)
            return render_html("class.html", posts=post_list[::-1], details=classroom_details, user_details = user_details, if_class_live = if_class_live)
app.route("access_classroom", access_classroom)

def categorized_posts(class_id):
    ret_code, user = validate_login(app.headers)
    if(ret_code == 0):
        return user
    else:
        ret_code, classroom_obj = validate_classroom(class_id, user)
        if(ret_code == 0):
            return classroom_obj
        posts = classroom_obj.list_posts(sql_database=sql_database)
        post_dict = {}
        for post in posts:
            tag_name = post.get_tag(sql_database)
            if tag_name not in post_dict:
                post_dict[tag_name] = [{"postID":post.postID, "classID":post.classID, "timestamp":post.timestamp, "creator_userID":post.creator_userID, "content":post.content, "tag":tag_name}]
            else:
                post_dict[tag_name].append({"postID":post.postID, "classID":post.classID, "timestamp":post.timestamp, "creator_userID":post.creator_userID, "content":post.content, "tag":tag_name})
        post_list = []
        for tag_name in post_dict:
            post_list.append({"tag": tag_name, "sorted_posts": post_dict[tag_name]})
        user_details = user_json(user)
        classroom_details = classroom_json(classroom_obj)
        if_class_live = LiveClass(classID=classroom_obj.classID).check_if_live(sql_database)
        return render_html("posts_by_tag.html", posts=post_list, details=classroom_details, user_details = user_details, if_class_live = if_class_live)

app.route("categorize", categorized_posts)

def access_students(class_id):
    ret_code, user = validate_login(app.headers)
    if(ret_code == 0):
        return user
    else:
        ret_code, classroom_obj = validate_classroom(class_id, user)
        if(ret_code == 0):
            return classroom_obj
        if(user.userID == classroom_obj.creator_userID):
            students_list = classroom_obj.list_students(sql_database)
            user_details = user_json(user)
            classroom_details = classroom_json(classroom_obj)
            if_class_live = LiveClass(classID=classroom_obj.classID).check_if_live(sql_database)
            return render_html("students.html", students_list = students_list, details=classroom_details, user_details = user_details, if_class_live = if_class_live)
        else:
            return error(200, "You are not an Instructor. Only instructors can view list of students in the Classroom")
app.route("access_students", access_students)

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

def end_classroom_session():
    ret_code, user = validate_login(app.headers)
    if(ret_code == 0):
        return user
    else:
        if(app.method == "POST"):
            classID = app.form_data["classID"]
            live_class = LiveClass(classID=classID)
            if_live = live_class.check_if_live(sql_database)
            if if_live:
                status = live_class.end_class(sql_database)
            return redirect("/classrooms/{}".format(classID))
        else:
            return error(405)
app.route("/end_class", end_classroom_session)


def join_live_class(classID):
    ret_code, user = validate_login(app.headers)
    if(ret_code == 0):
        return user
    else:
        if app.method == "GET":
            ret_code, classroom_obj = validate_classroom(classID, user)
            if(ret_code == 0):
                return classroom_obj
            live_class = LiveClass(classID=classID)
            if_live = live_class.check_if_live(sql_database)
            if not if_live:
                return error(400, "The class has not started yet.")
            user_attendance = Attendance(liveclassID=live_class.liveclassID, userID=user.userID, classID = classroom_obj.classID)
            user_attendance.mark_attendance(sql_database)
            user_details = user_json(user)
            classroom_details = Classroom(classID=classID).get_class_details(sql_database)
            return render_html("live_class.html", live_class = live_class, user_attendance = user_attendance, user_details=user_details, details=classroom_details, if_class_live = if_live)
        else:
            return error(405)
app.route("join_live_class", join_live_class)

def show_attendace(classID):
    ret_code, user = validate_login(app.headers)
    if(ret_code == 0):
        return user
    else:
        if app.method == "GET":
            ret_code, classroom_obj = validate_classroom(classID, user)
            if(ret_code == 0):
                return classroom_obj
            user_details = user_json(user)
            attendance = classroom_obj.get_attendance(sql_database)
            classroom_details = classroom_json(classroom_obj)
            if_class_live = LiveClass(classID=classroom_obj.classID).check_if_live(sql_database)
            return render_html("attendance.html", final_tally = attendance, user_details=user_details, details=classroom_details, if_class_live = if_class_live)
        else:
            return error(405)
app.route("attendance", show_attendace)

def discussions(class_id):
    ret_code, user = validate_login(app.headers)
    if(ret_code == 0):
        return user
    else:
        ret_code, classroom_obj = validate_classroom(class_id, user)
        if(ret_code == 0):
            return classroom_obj
        # print("class ID is:", class_id)
        if app.method == "POST":
            if(user.userID == classroom_obj.creator_userID):
                form_data = app.form_data
                gd_topic = form_data["gd_topic"]
                gd = Group_discussion(classID=classroom_obj.classID, gd_topic=gd_topic)
                gd.add_gd(sql_database)
                # print("classroom_obj", classroom_obj)
                return redirect("/classrooms/{}/group_discussions".format(class_id))
            else:
                return error(200, "You are not a Instructor. Only instructors can create a Group Discussion on Classroom")
        else:
            group_discussions = classroom_obj.get_group_discussions(sql_database)
            gd_list = []
            for gd in group_discussions:
                gd_list.append({"gdID":gd.gdID, "classID":gd.classID, "gd_topic":gd.gd_topic})
            user_details = user_json(user)
            classroom_details = classroom_json(classroom_obj)
            if_class_live = LiveClass(classID=classroom_obj.classID).check_if_live(sql_database)
            return render_html("group_discussions.html", gd_list=gd_list, user_details = user_details, details=classroom_details, if_class_live = if_class_live)
app.route("discussions", discussions)


def access_discussion(gdID, class_id):
    ret_code, user = validate_login(app.headers)
    if(ret_code == 0):
        return user
    else:
        ret_code, classroom_obj = validate_classroom(class_id, user)
        if(ret_code == 0):
            return classroom_obj
        gd_list = classroom_obj.get_group_discussions(sql_database)
        gd_obj = None
        gdIDs = [gd.gdID for gd in gd_list]
        if gdID not in gdIDs:
            return error(200, "Group discussion not found in this classroom")
        for gd in gd_list:
            if gd.gdID == gdID:
                gd_obj = gd
                break
        instructor = (user.userID == classroom_obj.creator_userID)
        print("GD_ID is - ", gd_obj.gdID)
        if app.method == "POST":
            form_data = app.form_data
            private = form_data["if_private"]
            if(private == "1"):
                # Private message
                if instructor:
                    studentID = form_data["receiver"]
                    private_msg = form_data["private_msg"]
                    private_msg_obj = GD_message(gdID=gd_obj.gdID, sender_userID=user.userID, private=studentID, content=private_msg)
                    private_msg_obj.add_msg(sql_database)
                else:
                    private_msg = form_data["private_msg"]
                    private_msg_obj = GD_message(gdID=gd_obj.gdID, sender_userID=user.userID, private=classroom_obj.creator_userID, content=private_msg)
                    private_msg_obj.add_msg(sql_database)
            else:
                # Public message
                public_msg = form_data["public_msg"]
                public_msg_obj = GD_message(gdID=gd_obj.gdID, sender_userID=user.userID, private=-1, content=public_msg)
                public_msg_obj.add_msg(sql_database)
            return redirect("/classrooms/{}/group_discussions/{}".format(class_id, gd_obj.gdID))

        else:
            public_list, tmp_private_list = gd_obj.get_messages(sql_database)
            for priv_msg in tmp_private_list:
                user_tmp_obj = User(userID = priv_msg["sender_userID"])
                username_tmp = user_tmp_obj.get_name_of_user(sql_database)
                # print(username_tmp)
                receiver_tmp_obj = User(userID = priv_msg["private"])
                priv_msg["recvname"] = receiver_tmp_obj.get_name_of_user(sql_database)
                priv_msg["username"] = username_tmp
                priv_msg["senderID"] = priv_msg["sender_userID"]
            for pub_msg in public_list:
                user_tmp_obj = User(userID = pub_msg["sender_userID"])
                username_tmp = user_tmp_obj.get_name_of_user(sql_database)
                # print(username_tmp)
                pub_msg["username"] = username_tmp
            private_list = []
            if instructor:
                # teacher view
                private_list = tmp_private_list
            else:
                # student view
                private_list = []
                for priv_msg in tmp_private_list:
                    if priv_msg["sender_userID"] == user.userID or priv_msg["private"] == user.userID:
                        private_list.append(priv_msg)
            user_details = user_json(user)
            classroom_details = classroom_json(classroom_obj)
            if_class_live = LiveClass(classID=classroom_obj.classID).check_if_live(sql_database)
            return render_html("discussion.html", private_list = private_list, public_list = public_list, is_instructor = instructor, gd_topic=gd_obj.gd_topic, gdID = gd_obj.gdID, user_details = user_details, details=classroom_details, if_class_live = if_class_live)
        
app.route("access_discussion", access_discussion)
