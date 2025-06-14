from app.models import db, Class

def get_all_classes():
    return Class.query.all()


def get_classes_by_teacher_id(teacher_id):
    return Class.query.filter_by(class_teacher_id=teacher_id).all()
