from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import VARCHAR

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(VARCHAR(120), unique=True, nullable=False)
    password_hash = db.Column(VARCHAR(128), nullable=False)
    role = db.Column(VARCHAR(20), nullable=False)  # 'student', 'teacher', 'parent', 'admin'
