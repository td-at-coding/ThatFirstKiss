from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class users(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.String(100))
    email = db.Column('email', db.String(100))
    sex = db.Column('sex', db.String(1))
    banned = db.Column('banned', db.Boolean, default=False)
    def __init__(self,name,email,sex):
        self.name = name
        self.email = email
        self.sex = sex

class images(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    img = db.Column('img', db.Text, unique=True)
    filename = db.Column('filename', db.Text)
    mimetype = db.Column('mimetype', db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    def __init__(self,img,filename,mimetype, user_id):
        self.img = img
        self.filename = filename
        self.mimetype = mimetype
        self.user_id = user_id

class matches(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    user_one_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user_two_id = db.Column(db.Integer, db.ForeignKey('users.id'))


    user_one = db.relationship('users', foreign_keys=[user_one_id])
    user_two = db.relationship('users', foreign_keys=[user_two_id])

    __table_args__ = (
        db.UniqueConstraint('user_one_id', 'user_two_id', name='unique_match'),
    )

    def __init__(self, user_one, user_two):
        self.user_one = user_one
        self.user_two = user_two

class messages(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    text = db.Column('text', db.String(100))
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    match_ = db.relationship('matches', foreign_keys=[match_id])
    user = db.relationship('users', foreign_keys=[user_id])

    def __init__(self,text,match_,user):
        self.text = text
        self.match_ = match_
        self.user = user

class requests(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    initiator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    initiator = db.relationship('users', foreign_keys=[initiator_id])
    receiver = db.relationship('users', foreign_keys=[receiver_id])

    __table_args__ = (
        db.UniqueConstraint('initiator_id', 'receiver_id', name='unique_request'),
    )

    def __init__(self,initiator,receiver):
        self.initiator = initiator
        self.receiver = receiver

class dislikes(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    disliked_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship('users', foreign_keys=[user_id])
    disliked = db.relationship('users', foreign_keys=[disliked_id])

    __table_args__ = (
        db.UniqueConstraint('user_id', 'disliked_id', name='unique_dislikes'),
    )
    def __init__(self,user,disliked):
        self.user = user
        self.disliked = disliked

# class reports(db.Model):
#     id = db.Column('id', db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
#     reporter_id = db.Column(db.Integer, db.ForeignKey('users.id'))
#     title = db.Column('title', db.String(100))
#     desc = db.Column('desc', db.String(500))

#     user = db.relationship('users', foreign_keys=[user_id])
#     reporter = db.relationship('users', foreign_keys=[reporter_id])

#     __table_args__ = (
#         db.UniqueConstraint('user_id', 'reporter_id', name='unique_reports'),
#     )

#     def __init__(self,title,desc,user,repoter):
#         self.title = title
#         self.desc = desc
#         self.user = user
#         self.repoter = repoter