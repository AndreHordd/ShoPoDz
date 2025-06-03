from app.models import Student, db

def get_students_for_class(class_id):
    return Student.query.filter_by(class_id=class_id).all()
