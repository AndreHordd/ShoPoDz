from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()

class Subject(db.Model):
    __tablename__ = 'subjects'

    subject_id            = db.Column(db.Integer, primary_key=True)
    title                 = db.Column(db.String(200), nullable=False)
    first_teaching_grade  = db.Column(db.SmallInteger, nullable=False)
    last_teaching_grade   = db.Column(db.SmallInteger, nullable=False)



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

class Homework(db.Model):
    __tablename__ = 'homework'
    homework_id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.lesson_id'), nullable=False)
    description = db.Column(db.Text)
    deadline = db.Column(db.DateTime)
    # НЕ ДОДАВАЙ lesson = db.relationship(...) — backref вже створює lesson в Homework

class Lesson(db.Model):
    __tablename__ = 'lessons'
    lesson_id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.class_id'), nullable=False)
    class_ = db.relationship('Class', backref='lessons')
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.room_id'), nullable=True)
    day = db.Column(db.SmallInteger, nullable=False)  # 1=Monday, ..., 7=Sunday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    # В Lesson — тільки тут зв'язок!
    homeworks = db.relationship("Homework", backref="lesson", lazy=True)
    subject = db.relationship("Subject", backref="lessons")

    # опціональні зв'язки:
    # class_ = db.relationship("Class", backref="lessons")
    # subject = db.relationship("Subject", backref="lessons")
    # teacher = db.relationship("User", backref="lessons")  # якщо в users всі вчителі

class Grade(db.Model):
    __tablename__ = 'grades'
    grade_id    = db.Column(db.Integer, primary_key=True)
    student_id  = db.Column(db.Integer, db.ForeignKey('students.user_id'), nullable=False)
    lesson_id   = db.Column(db.Integer, db.ForeignKey('lessons.lesson_id'),  nullable=False)
    teacher_id  = db.Column(db.Integer, db.ForeignKey('users.user_id'),    nullable=False)
    grade_value = db.Column(db.SmallInteger, nullable=False)
    comment     = db.Column(db.Text)
    # прибрати цю строку:
    # date_set    = db.Column(db.DateTime, default=datetime.utcnow)

