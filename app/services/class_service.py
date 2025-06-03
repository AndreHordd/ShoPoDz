from app.dao.classes_dao import get_all_classes
from app.dao.students_dao import get_students_for_class
def fetch_all_classes():
    return get_all_classes()


def get_students_by_class_id(class_id):
    return get_students_for_class(class_id)
