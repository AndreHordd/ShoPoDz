from app.models import Student, db
from app.utils.db import get_db

def get_students_for_class(class_id):
    return Student.query.filter_by(class_id=class_id).all()

def get_student_by_parent(parent_id: int):
    """
    Повертає словник із даними учня, прив’язаного до даного батька,
    включно з class_id.
    """
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
      SELECT user_id, first_name, last_name, class_id
      FROM students
      WHERE parent_id = %s
    """, (parent_id,))
    row = cur.fetchone()
    cur.close()
    if not row:
        return None
    return {
        'user_id':   row[0],
        'first_name':row[1],
        'last_name': row[2],
        'class_id':  row[3]
    }