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

    def add_class(self, sql_database):
        
        db_cursor = sql_database.cursor()
        sql = '''INSERT INTO Classrooms (creator_userID, name, description) VALUES (%s, %s, %s)'''
        val = (self.creator_userID, self.name, self.description)
        db_cursor.execute(sql, val)
        db_cursor.commit()
        self.classID = db_cursor.lastrowid
        code = joining_code_from_id(self.classID)
        db_cursor.execute('''UPDATE Classrooms SET code = %s WHERE classID = %s''', (code, self.classID))
        db_cursor.commit()
        db_cursor.close()
    
    def get_id_from_code(self, sql_database):

        db_cursor = sql_database.cursor()
        sql = '''SELECT classID FROM Classrooms WHERE code = %s'''
        db_cursor.execute(sql, (self.joining_code,))
        results = db_cursor.fetchall()
        # assert(len(results) == 1)
        return int(results[0][0])

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
    
    def add_role(self, sql_database):

        db_cursor = sql_database.cursor()
        sql = '''INSERT INTO ClassUserRole (classID, userID, role)  VALUES (%s, %s, %s)'''
        val = (self.classID, self.userID, self.role)
        db_cursor.execute(sql, val)
        db_cursor.commit()
        db_cursor.close()

# Can be Implemented using JOIN in sql
#  
# class Tag_post_map:
#     def __init__(self, postID, tagID):
#         self.postID = postID
#         self.tagID = tagID
        
        
