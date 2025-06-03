from app.models import db, Class

def get_classes_by_teacher_id(teacher_id):
    return (
        db.session.query(Class.class_number, Class.subclass)
        .filter(Class.class_teacher_id == teacher_id)
        .all()
    )
