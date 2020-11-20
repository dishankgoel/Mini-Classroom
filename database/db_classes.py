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
    def __init__(self, userID, emailID, password, name):
        self.userID = userID
        self.emailID = emailID
        self.password = password
        self.name = name

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
        
        
