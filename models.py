import hashlib

def joining_code_from_id(classID):
    return hashlib.md5(bytes(str(classID), "utf-8")).hexdigest()[:8]
    
def gen_session_code(liveclassID, userID):
    return hashlib.md5(bytes(str(liveclassID) + "::" + str(userID), "utf-8")).hexdigest()[:10]

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
        self.creator_userID = results[0][1]
        creator_name = self.get_creator_name(sql_database)[0][0]
        details = { "classID": self.classID, "creator_userID": results[0][1], "name": results[0][2], "description": results[0][3], "joining_code": results[0][4], "creator_name": creator_name}
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

    def get_group_discussions(self, sql_database):
        sql = "SELECT * from GroupDiscussions WHERE classID = %s"
        db_cursor = sql_database.cursor()
        db_cursor.execute(sql, (self.classID,))
        gds = db_cursor.fetchall()
        gd_list = []
        for gd in gds:
            gd_list.append(Group_discussion(gdID=gd[0], classID=gd[1], gd_topic=gd[2]))
        return gd_list

    def get_creator_name(self, sql_database):
        db_cursor = sql_database.cursor()
        creator_name_sql = "SELECT name from Users WHERE userID=%s"
        db_cursor.execute(creator_name_sql, (self.creator_userID,))
        creator_name = db_cursor.fetchall()
        db_cursor.close()
        return creator_name

    def list_students(self, sql_database):
        sql = "SELECT userID from ClassUserRole where ClassID = %s AND role != %s"
        db_cursor = sql_database.cursor()
        db_cursor.execute(sql, (self.classID,0))
        students_list = db_cursor.fetchall()
        student_info = []
        db_cursor.close()
        for student_tup in students_list:
            studentID = student_tup[0]
            student_obj = User(userID=studentID)
            student_name = student_obj.get_name_of_user(sql_database=sql_database)
            student_info.append({"userID": studentID, "Name": student_name})
        return student_info
    
    def get_attendance(self, sql_database):
        db_cursor = sql_database.cursor()
        sql = '''SELECT * FROM Attendance WHERE classID = %s'''
        db_cursor.execute(sql, (self.classID, ))
        results = db_cursor.fetchall()
        db_cursor.close()
        all_students = self.list_students(sql_database)
        classes_attended = {}
        names = {}
        for student in all_students:
            classes_attended[student["userID"]] = set()
            names[student["userID"]] = student["Name"]
        total_classes = set()
        for attendance in results:
            liveclassID = attendance[1]
            total_classes.add(liveclassID)
            user_id = attendance[2]
            if user_id != self.creator_userID:
                classes_attended[user_id].add(liveclassID)
        final_tally = []
        total_classes_len = len(total_classes)
        for user_id in classes_attended:
            attended = len(classes_attended[user_id])
            data = {"name": names[user_id], "total": total_classes_len, "attended": attended}
            final_tally.append(data)
        final_tally.sort(key=lambda x: x["attended"])
        return final_tally


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
        # Query for getting all the classrooms
        values = [str(i[0]) for i in results]
        query = '''SELECT * from Classrooms where classID IN ({})'''.format(", ".join(values))
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

    def __init__(self, liveclassID=None, classID=None, timestamp = None):

        self.liveclassID = liveclassID
        self.classID = classID
        self.timestamp = timestamp
    
    def check_if_live(self, sql_database):
        db_cursor = sql_database.cursor()
        sql = '''SELECT * FROM LiveClass WHERE classID = %s'''
        db_cursor.execute(sql, (self.classID,))
        results = db_cursor.fetchall()
        db_cursor.close()
        if(len(results) > 0):
            self.liveclassID = results[0][0]
            self.timestamp = results[0][2]
            return 1
        return 0

    def start(self, sql_database):

        if_live = self.check_if_live(sql_database)
        if not if_live:
            db_cursor = sql_database.cursor()
            sql = '''INSERT INTO LiveClass (classID) VALUES (%s)'''
            db_cursor.execute(sql, (self.classID,))
            sql_database.commit()
            self.liveclassID = db_cursor.lastrowid
            db_cursor.close()
            return 1
        return 0
    
    def end_class(self, sql_database):

        db_cursor = sql_database.cursor()
        sql = '''DELETE FROM LiveClass WHERE classID = %s'''
        db_cursor.execute(sql, (self.classID,))
        sql_database.commit()
        sql_database.commit()
        db_cursor.close()
        return 1

class Attendance:

    def __init__(self, attendaceID = None, liveclassID = None, userID = None, classID = None, sessionID = None, timestamp = None):

        self.attendaceID = attendaceID
        self.liveclassID = liveclassID
        self.userID = userID
        self.classID = classID
        self.sessionID = sessionID
        self.timestamp = timestamp

    def mark_attendance(self, sql_database):

        db_cursor = sql_database.cursor()
        self.sessionID = gen_session_code(self.liveclassID, self.userID)
        sql = '''SELECT * from Attendance WHERE liveclassID = %s AND userID = %s'''
        val = (self.liveclassID, self.userID)
        db_cursor.execute(sql, val)
        results = db_cursor.fetchall()
        if(len(results) == 0):
            sql = '''INSERT INTO Attendance (liveclassID, userID, classID, sessionID) VALUES (%s, %s, %s, %s)'''
            val = (self.liveclassID, self.userID, self.classID, self.sessionID)
            db_cursor.execute(sql, val)
            sql_database.commit()
        db_cursor.close()

    def validate_sessionID(self, sql_database):

        db_cursor = sql_database.cursor()
        sql = '''SELECT * FROM Attendance WHERE sessionID = %s'''
        db_cursor.execute(sql, (self.sessionID, )) 
        results = db_cursor.fetchall()
        if(len(results) == 0):
            return 0
        self.liveclassID = results[0][1] 
        code_userID = results[0][2]
        if(int(code_userID) != int(self.userID)):
            return 0
        self.timestamp = results[0][4]
        db_cursor.execute('''SELECT * from LiveClass WHERE liveclassID = %s''', (self.liveclassID, ))
        results = db_cursor.fetchall()
        db_cursor.close()
        if(len(results) == 0):
            return 0
        return 1
    
class Group_discussion:
    def __init__(self, classID=None, gdID=None, gd_topic=None):
        self.gdID = gdID
        self.classID = classID
        self.gd_topic = gd_topic

    def add_gd(self, sql_database):
        db_cursor = sql_database.cursor()
        sql = '''INSERT INTO GroupDiscussions (classID, gdTopic) VALUES (%s, %s)'''
        val = (self.classID, self.gd_topic)
        db_cursor.execute(sql, val)
        sql_database.commit()
        db_cursor.close()

    def get_messages(self, sql_database):
        db_cursor = sql_database.cursor()
        sql = '''SELECT * FROM GDMessages WHERE gdID = %s'''
        db_cursor.execute(sql, (self.gdID,))
        msgs = db_cursor.fetchall()
        private_list = []
        public_list = []
        print("msgs:", msgs)
        for msg in msgs:
            if msg[4]==-1:
                public_list.append({"msgID":msg[0], "gdID":msg[1], "sender_userID":msg[2], "timestamp":msg[3], "private":msg[4], "content":msg[5]})
            else:
                private_list.append({"msgID":msg[0], "gdID":msg[1], "sender_userID":msg[2], "timestamp":msg[3], "private":msg[4], "content":msg[5]})
                
        db_cursor.close()
        return public_list, private_list

class GD_message:
    def __init__(self, msgID=None, gdID=None, sender_userID=None, timestamp=None, private=None, content=None):
        self.msgID = msgID
        self.gdID = gdID
        self.sender_userID = sender_userID
        self.timestamp = timestamp
        self.private = private
        self.content = content

    def add_msg(self, sql_database):
        db_cursor = sql_database.cursor()
        sql = '''INSERT INTO GDMessages (gdID, sender_userID, private, content) VALUES (%s, %s, %s, %s)'''
        val = (self.gdID, self.sender_userID, self.private, self.content)
        db_cursor.execute(sql, val)
        sql_database.commit()
        db_cursor.close()