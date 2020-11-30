import mysql.connector

'''
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root';
'''

conn = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "Proj@Py19"
)

dbcursor = conn.cursor()

dbcursor.execute("CREATE DATABASE MiniClassroom")

dbcursor.execute("use MiniClassroom")

make_classrooms = '''CREATE TABLE Classrooms (
    classID INT AUTO_INCREMENT PRIMARY KEY, 
    creator_userID INT,
    name VARCHAR(100),
    description TEXT,
    code VARCHAR(100) UNIQUE
)'''

make_posts = '''CREATE TABLE Posts (
    postID INT AUTO_INCREMENT PRIMARY KEY,
    classID INT,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    creator_userID INT,
    content TEXT
)'''

make_users = '''CREATE TABLE Users (
    userID INT AUTO_INCREMENT PRIMARY KEY,
    emailID VARCHAR(100) UNIQUE,
    password VARCHAR(100),
    name VARCHAR(100)
)'''

make_comments = '''CREATE TABLE Comments (
    commentID INT AUTO_INCREMENT PRIMARY KEY,
    postID INT,
    creator_userID INT,
    timestamp DATE,
    content TEXT
)'''

make_tags = '''CREATE TABLE PostTags (
    tagID INT AUTO_INCREMENT PRIMARY KEY,
    tagName VARCHAR(100),
    postID INT,
    classID INT
)'''

make_classroom_user_role = '''CREATE TABLE ClassUserRole (
    classID INT,
    userID INT,
    role INT
)'''

make_group_discussions = '''CREATE TABLE GroupDiscussions (
    gdID INT AUTO_INCREMENT PRIMARY KEY,
    classID INT,
    gdTopic VARCHAR(100)    
)'''

make_gd_messages = '''CREATE TABLE GDMessages (
    msgID INT AUTO_INCREMENT PRIMARY KEY,
    gdID INT,
    sender_userID INT,
    timestamp DATE,
    private INT,
    content VARCHAR(100)
)'''

sql_queries = [make_classrooms, make_posts, make_users, make_comments, make_tags, make_classroom_user_role, make_group_discussions, make_gd_messages]

for query in sql_queries:
    dbcursor.execute(query)

conn.close()