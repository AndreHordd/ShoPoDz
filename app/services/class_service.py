from app.dao.students_dao import get_students_for_class
from app.utils.db import get_db
from collections import namedtuple

def fetch_all_classes():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT class_id, class_number, subclass, class_teacher_id
        FROM classes
        ORDER BY class_number, subclass
    """)
    rows = cur.fetchall()
    cur.close()

    # Поверни об'єкти з class_teacher_id
    return [
        {
            "class_id": r[0],
            "class_number": r[1],
            "subclass": r[2],
            "class_teacher_id": r[3]
        } for r in rows
    ]


def get_students_by_class_id(class_id):
    return get_students_for_class(class_id)
