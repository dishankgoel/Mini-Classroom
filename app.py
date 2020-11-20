import os
from server_to_app import Interface, redirect, render_html, not_found
import mysql.connector


app = Interface()

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

# def login():
#     return render_html("login.html")

def signup():
    if app.method == "GET":
        return render_html("signup.html")
    elif app.method == "POST":
        form_data = app.form_data
        name = form_data["name"]
        email = form_data["email"]
        passwd = form_data["pwd"]
        db_cursor = sql_database.cursor()
        try:
            sql = "INSERT INTO Users (emailID, password, name) VALUES (%s, %s, %s)"
            val = (email, passwd, name)
            db_cursor.execute(sql, val)
            sql_database.commit()
        except:
            not_found()
        return render_html("index.html")

app.route("/signup", signup)