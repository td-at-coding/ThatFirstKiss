from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class users(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.String(100))
    email = db.Column('email', db.String(100))
    sex = db.Column('sex', db.String(1))
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
