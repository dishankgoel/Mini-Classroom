class Classroom:
    def __init__(self, classID=None, creator_userID=None, name=None, description=None):
        self.classID = classID
        self.creator_userID = creator_userID
        self.name = name
        self.description = description

    def list_posts(self, sql_database):
        sql = "SELECT * from Posts WHERE CLASSID=%s"
        db_cursor = sql_database.cursor()
        db_cursor.execute(sql, (self.classID,))
        posts = db_cursor.fetchall()        
        return posts

    def get_creator_name(self, sql_database):
        db_cursor = sql_database.cursor()
        creator_name_sql = "SELECT name from Users WHERE userID=%s"
        db_cursor.execute(creator_name_sql, (self.creator_userID,))
        creator_name = db_cursor.fetchall()
        return creator_name

class Post:
    def __init__(self, postID, classID, timestamp, creator_userID, content):
        self.postID = postID
        self.classID = classID
        self.timestamp = timestamp
        self.creator_userID = creator_userID
        self.content = content

class User:
    def __init__(self, emailID = None, password = None, name = None, userID = None):
        self.userID = userID
        self.emailID = emailID
        self.password = password
        self.name = name

    def add_user(self, sql_database):
        
        db_cursor = sql_database.cursor()
        # Check if user exists
        db_cursor.execute('''SELECT emailID from Users''')
        results = db_cursor.fetchall()
        if (self.emailID,) in results:
            return -1
        # Insert the user
        sql = "INSERT INTO Users (emailID, password, name) VALUES (%s, MD5(%s), %s)"
        val = (self.emailID, self.password, self.name)
        db_cursor.execute(sql, val)
        sql_database.commit()
        user_id = db_cursor.lastrowid
        db_cursor.close()
        return user_id

    def login_user(self, sql_database):

        db_cursor = sql_database.cursor()
        # Get this users details if it exists
        query = '''SELECT * from Users where emailID = %s and password = MD5(%s)'''
        val = (self.emailID, self.password)
        db_cursor.execute(query, val)
        results = db_cursor.fetchall()
        db_cursor.close()
        if(len(results) == 1):
            user_id = results[0][0]
            name = results[0][3]
            return user_id, name
        else:
            return 0

    def list_classrooms(self, sql_database):

        db_cursor = sql_database.cursor()
        query = '''SELECT * FROM ClassUserRole where userID = %s'''
        db_cursor.execute(query, (self.userID,))
        results = db_cursor.fetchall()
        if(len(results) == 0):
            return []
        # user_roles = [Classroom_user_role(classID=int(i[0]), userID=self.userID, role=int(i[2])) for i in results]
        # Query for getting all the classrooms
        values = [str(i[0]) for i in results]
        query = '''SELECT * from Classrooms where classID IN ({})'''.format(", ".join(values))
        # for user_role in user_roles[1:]:
        #     query += " OR classID = {}".format(user_role.classID)
        db_cursor.execute(query)
        results = db_cursor.fetchall()
        joined_classrooms = []
        for result in results:
            joined_classrooms.append(Classroom(classID=int(result[0]), creator_userID=int(result[1]), name=result[2], description=result[3]))
        db_cursor.close()
        return joined_classrooms



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
        
        
