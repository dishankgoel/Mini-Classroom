class Classroom:
    def __init__(self, classID, creator_userID, name):
        self.classID = classID
        self.creator_userID = creator_userID
        self.name = name

class Post:
    def __init__(self, postID, classID, timestamp, creator_userID, content):
        self.postID = postID
        self.classID = classID
        self.timestamp = timestamp
        self.creator_userID = creator_userID
        self.content = content

class User:
    def __init__(self, emailID = None, password = None, name = None):
        # self.userID = userID // for internal usage
        self.emailID = emailID
        self.password = password
        self.name = name

    def add_user(self, sql_database):
        
        db_cursor = sql_database.cursor()
        # Check if user exists
        db_cursor.execute('''SELECT emailID from Users''')
        results = db_cursor.fetchall()
        if self.emailID in results:
            return 0
        
        # Insert the user
        sql = "INSERT INTO Users (emailID, password, name) VALUES (%s, MD5(%s), %s)"
        val = (self.emailID, self.password, self.name)
        db_cursor.execute(sql, val)
        sql_database.commit()
        db_cursor.close()
        return 1

    def login_user(self, sql_database):

        db_cursor = sql_database.cursor()
        # Get this users details if it exists
        query = '''SELECT * from Users where name = %s and password = MD5(%s)'''
        val = (self.name, self.password)
        db_cursor.execute(query, val)
        results = db_cursor.fetchall()
        if(len(results) == 1):
            return 1
        else:
            return 0

class Comment:
    def __init__(self, commentID, postID, creator_userID, timestamp, content):
        self.commentID = commentID
        self.postID = postID
        self.creator_userID = creator_userID
        self.timestamp = timestamp
        self.content = content

class Tag:
    def __init__(self, tagID, tagName, classID):
        self.tagID = tagID
        self.tagName = tagName
        self.classID = classID

class Classroom_user_role:
    def __init__(self, classID, userID, role):
        self.classID = classID
        self.userID = userID
        self.role = role

# Can be Implemented using JOIN in sql
#  
# class Tag_post_map:
#     def __init__(self, postID, tagID):
#         self.postID = postID
#         self.tagID = tagID
        
        
