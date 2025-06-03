from app.dao.classes_dao import get_all_classes
from app.models import Student


from app.dao.students_dao import get_students_for_class
def fetch_all_classes():
    return get_all_classes()


def get_students_by_class_id(class_id):
    # Повертаємо список учнів, відсортований за last_name (прізвище)
    return Student.query.filter_by(class_id=class_id).order_by(Student.last_name.asc()).all()
