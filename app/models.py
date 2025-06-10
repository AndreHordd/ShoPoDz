from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
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


class Homework(db.Model):
    __tablename__ = 'homework'
    homework_id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)
    deadline    = db.Column(db.DateTime)
    session_id  = db.Column(db.Integer, db.ForeignKey('lesson_sessions.session_id'), nullable=False)

class LessonSession(db.Model):
    __tablename__ = 'lesson_sessions'
    session_id   = db.Column(db.Integer, primary_key=True)
    lesson_id    = db.Column(db.Integer, db.ForeignKey('lessons.lesson_id'), nullable=False)
    session_date = db.Column(db.Date, nullable=False)
    lesson       = db.relationship('Lesson', backref='sessions', lazy=True)

class Grade(db.Model):
    __tablename__ = 'grades'
    grade_id    = db.Column(db.Integer, primary_key=True)
    student_id  = db.Column(db.Integer, db.ForeignKey('students.user_id'), nullable=False)
    teacher_id  = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    grade_value = db.Column(db.SmallInteger, nullable=False)
    comment     = db.Column(db.Text)
    session_id  = db.Column(db.Integer, db.ForeignKey('lesson_sessions.session_id'), nullable=False)
    # lesson_id -- НЕ треба!
    session = db.relationship('LessonSession', backref='grades', lazy=True)

class Attendance(db.Model):
    __tablename__ = 'attendance'  # або 'attendances', якщо у вашій БД саме так

    attendance_id = db.Column(db.Integer, primary_key=True)
    student_id    = db.Column(db.Integer, db.ForeignKey('students.user_id'), nullable=False)
    lesson_id     = db.Column(db.Integer, db.ForeignKey('lessons.lesson_id'),  nullable=False)
    status        = db.Column(db.String(20), nullable=False)  # наприклад, 'present', 'absent' тощо
    comment       = db.Column(db.Text)

    # Зв’язки для зручності:
    student = db.relationship('Student', backref='attendances', lazy=True)
    lesson  = db.relationship('Lesson',  backref='attendances', lazy=True)


class ParentSignature(db.Model):
    """
    Прив’язка SQLAlchemy до вже створеної таблиці signatures.
    """
    __tablename__ = "signatures"          # ← ваша назва

    signature_id = db.Column(db.Integer, primary_key=True)
    parent_id    = db.Column(db.Integer,
                             db.ForeignKey("parents.user_id",
                                           ondelete="CASCADE"),
                             nullable=False)
    student_id   = db.Column(db.Integer,
                             db.ForeignKey("students.user_id",
                                           ondelete="CASCADE"),
                             nullable=False)
    signed_at    = db.Column(db.DateTime,
                             nullable=False,
                             default=datetime.utcnow)

    # унікальність по всьому timestamp залишаємо — дубль малоймовірний


class Message(db.Model):
    __tablename__ = 'messages'

    message_id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    text = db.Column(db.Text, nullable=False)

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')

class Parent(db.Model):
    __tablename__ = 'parents'

    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    # (інші потрібні поля)

class Teacher(db.Model):
    __tablename__ = 'teachers'
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    salary = db.Column(db.Numeric(10,2), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    hire_date = db.Column(db.Date, nullable=False)

    user = db.relationship('User', backref='teacher', uselist=False)



class Lesson(db.Model):
    __tablename__ = 'lessons'
    lesson_id     = db.Column(db.Integer, primary_key=True)
    class_id      = db.Column(db.Integer, db.ForeignKey('classes.class_id'), nullable=False)
    subject_id    = db.Column(db.Integer, db.ForeignKey('subjects.subject_id'), nullable=False)
    teacher_id    = db.Column(db.Integer, db.ForeignKey('teachers.user_id'), nullable=False)
    day           = db.Column(db.SmallInteger, nullable=False)  # ← ДОДАЙ!
    start_time    = db.Column(db.Time, nullable=False)
    end_time      = db.Column(db.Time, nullable=False)
    class_        = db.relationship('Class', backref='lessons')
    subject       = db.relationship('Subject', backref='lessons')

class Student(db.Model):
    __tablename__ = 'students'
    user_id     = db.Column(db.Integer, primary_key=True)
    first_name  = db.Column(db.String(100), nullable=False)
    last_name   = db.Column(db.String(100), nullable=False)
    class_id    = db.Column(db.Integer, db.ForeignKey('classes.class_id'), nullable=False)

class Class(db.Model):
    __tablename__ = 'classes'
    class_id     = db.Column(db.Integer, primary_key=True)
    class_number = db.Column(db.SmallInteger, nullable=False)
    subclass     = db.Column(db.String(1), nullable=False)
    class_teacher_id = db.Column(db.Integer)   # ← ДОДАЙ ЦЕ!

