from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import VARCHAR

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)

class Class(db.Model):
    __tablename__ = 'classes'

    class_id = db.Column(db.Integer, primary_key=True)
    class_number = db.Column(db.Integer, nullable=False)
    subclass = db.Column(db.String(1), nullable=False)
    class_teacher_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

class Student(db.Model):
    __tablename__ = 'students'

    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    class_id = db.Column(db.Integer, db.ForeignKey('classes.class_id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.user_id'), nullable=False)
