import hashlib

def joining_code_from_id(classID):
    return hashlib.md5(bytes(str(classID), "utf-8")).hexdigest()[:8]
class Classroom:
    def __init__(self, classID=None, creator_userID=None, name=None, description=None, joining_code = None):
        self.classID = classID
        self.creator_userID = creator_userID
        self.name = name
        self.description = description
        self.joining_code = joining_code

    def get_class_details(self, sql_database):

        db_cursor = sql_database.cursor()
        sql = '''SELECT * from Classrooms WHERE classID = %s'''
        db_cursor.execute(sql, (self.classID,))
        results = db_cursor.fetchall()
        db_cursor.close()
        details = { "classID": self.classID, "creator_userID": results[0][1], "name": results[0][2], "description": results[0][3], "joining_code": results[0][4]}
        return details


    def add_class(self, sql_database):
        
        db_cursor = sql_database.cursor()
        sql = '''INSERT INTO Classrooms (creator_userID, name, description) VALUES (%s, %s, %s)'''
        val = (self.creator_userID, self.name, self.description)
        db_cursor.execute(sql, val)
        sql_database.commit()
        self.classID = db_cursor.lastrowid
        code = joining_code_from_id(self.classID)
        db_cursor.execute('''UPDATE Classrooms SET code = %s WHERE classID = %s''', (code, self.classID))
        sql_database.commit()
        db_cursor.close()
    
    def get_id_from_code(self, sql_database):

        db_cursor = sql_database.cursor()
        sql = '''SELECT classID FROM Classrooms WHERE code = %s'''
        db_cursor.execute(sql, (self.joining_code,))
        results = db_cursor.fetchall()
        db_cursor.close()
        # assert(len(results) == 1)
        return int(results[0][0])

    def list_posts(self, sql_database):
        sql = "SELECT * from Posts WHERE CLASSID=%s"
        db_cursor = sql_database.cursor()
        db_cursor.execute(sql, (self.classID,))
        posts = db_cursor.fetchall()
        db_cursor.close()
        posts_list = []
        for post in posts:
            posts_list.append(Post(postID=post[0], classID=post[1], timestamp=post[2], creator_userID=post[3], content=post[4]))
        return posts_list

    def get_creator_name(self, sql_database):
        db_cursor = sql_database.cursor()
        creator_name_sql = "SELECT name from Users WHERE userID=%s"
        db_cursor.execute(creator_name_sql, (self.creator_userID,))
        creator_name = db_cursor.fetchall()
        db_cursor.close()
        return creator_name

class Post:
    def __init__(self, postID=None, classID=None, timestamp=None, creator_userID=None, content=None):
        self.postID = postID
        self.classID = classID
        self.timestamp = timestamp
        self.creator_userID = creator_userID
        self.content = content

    def add_post(self, sql_database):
        db_cursor = sql_database.cursor()
        sql = "INSERT INTO Posts (classID, creator_userID, content) VALUES (%s, %s, %s)"
        val = (self.classID, self.creator_userID, self.content)
        db_cursor.execute(sql, val)
        sql_database.commit()
        self.postID = db_cursor.lastrowid
        db_cursor.close()
        # look into tagID classID postID relation before going ahead
    
    def get_tag(self, sql_database):

        db_cursor = sql_database.cursor()
        sql = '''SELECT tagName from PostTags WHERE postID = %s AND classID = %s'''
        val = (self.postID, self.classID)
        db_cursor.execute(sql, val)
        results = db_cursor.fetchall()
        db_cursor.close()
        if(len(results) == 1):
            return results[0][0]

class User:
    def __init__(self, emailID = None, password = None, name = None, userID = None):
        self.userID = userID
        self.emailID = emailID
        self.password = password
        self.name = name
    
    def get_name_of_user(self, sql_database):

        db_cursor = sql_database.cursor()
        db_cursor.execute('''SELECT name from Users WHERE userID = %s''', (self.userID,))
        results = db_cursor.fetchall()
        db_cursor.close()
        return results[0][0]

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
            joining_code = joining_code_from_id(int(result[0])) 
            joined_classrooms.append(Classroom(classID=int(result[0]), creator_userID=int(result[1]), name=result[2], description=result[3], joining_code=joining_code))
        db_cursor.close()
        return joined_classrooms

class Tag:
    def __init__(self, tagID=None, tagName=None, postID=None, classID=None):
        self.tagID = tagID
        self.tagName = tagName
        self.postID = postID
        self.classID = classID
    
    def add_tag(self, sql_database):
        db_cursor = sql_database.cursor()
        sql = '''INSERT INTO PostTags (tagName, postID, classID) VALUES (%s, %s, %s)'''
        val = (self.tagName, self.postID, self.classID)
        db_cursor.execute(sql, val)
        sql_database.commit()
        self.tagID = db_cursor.lastrowid
        db_cursor.close()

    def list_posts_under_tag(self, sql_database):
        db_cursor = sql_database.cursor()
        sql = '''SELECT * from Posts INNER JOIN PostTags ON Posts.classID = PostTags.classID AND PostTags.tagName = %s'''
        db_cursor.execute(sql, (self.tagName,))
        results = db_cursor.fetchall()
        db_cursor.close()
        posts_list = []
        for post in results:
            posts_list.append(Post(postID=post[0], classID=post[1], timestamp=post[2], creator_userID=post[3], content=post.content))
        return posts_list


class Classroom_user_role:
    def __init__(self, classID, userID, role):
        self.classID = classID
        self.userID = userID
        self.role = role
    
    def add_role(self, sql_database):

        db_cursor = sql_database.cursor()
        sql = '''INSERT INTO ClassUserRole (classID, userID, role)  VALUES (%s, %s, %s)'''
        val = (self.classID, self.userID, self.role)
        db_cursor.execute(sql, val)
        sql_database.commit()
        db_cursor.close()

class LiveClass:

    def __init__(self, liveclassID=None, classID=None):

        self.liveclassID = liveclassID
        self.classID = classID
    
    def check_if_live(self, sql_database):
        
        db_cursor = sql_database.cursor()
        sql = '''SELECT * FROM LiveClass WHERE classID = %s'''
        db_cursor.execute(sql, (self.classID,))
        results = db_cursor.fetchall()
        db_cursor.close()
        if(len(results) > 0):
            self.liveclassID = results[0][0]
            return 1
        return 0

    def start(self, sql_database):

        if_live = self.check_if_live(sql_database)
        if not if_live:
            db_cursor = sql_database.cursor()
            sql = '''INSERT INTO LiveClass (classID) VALUES (%s)'''
            db_cursor.execute(sql, (self.classID,))
            sql_database.commit()
            db_cursor.close()
            return 1
        return 0
    
    def end_class(self, sql_database):

        db_cursor = sql_database.cursor()
        sql = '''DELETE FROM LiveClass WHERE classID = %s'''
        db_cursor.execute(sql, (self.classID,))
        sql_database.commit()
        db_cursor.close()
        
class LiveMessages:

    def __init__(self, livemessageID = None, liveclassID = None, userID = None, content = None, timestamp = None):

        self.livemessageID = livemessageID
        self.liveclassID = liveclassID
        self.userID = userID
        self.content = content
        self.timestamp = timestamp
        self.all_messages = []

    def get_all_messages(self, sql_database):

        db_cursor = sql_database.cursor()
        sql = '''SELECT * from LiveMessages WHERE liveclassID = %s'''
        db_cursor.execute(sql, (self.liveclassID,))
        results = db_cursor.fetchall()
        for result in results:
            userid, content, timestamp = result[2], result[3], result[4]
            name = User(userID=userid).get_name_of_user(sql_database)
            data = {"name": name, "content": content, "timestamp": timestamp}
            self.all_messages.append(data)

    def send_message(self, sql_database):

        db_cursor = sql_database.cursor()
        sql = '''INSERT INTO LiveMessages (liveclassID, userID, content) VALUES (%s, %s, %s)'''
        val = (self.liveclassID, self.userID, self.content)
        db_cursor.execute(sql, val)
        sql_database.commit()
        db_cursor.close()


        