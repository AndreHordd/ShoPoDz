from flask import Blueprint, request, jsonify
from app.utils.db import get_db

subject_bp = Blueprint('subject', __name__)

@subject_bp.route('/api/subjects/for-class/<int:class_number>')
def get_subjects_for_class(class_number):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT subject_id, title
        FROM subjects
        WHERE first_teaching_grade <= %s AND last_teaching_grade >= %s
        ORDER BY title
    """, (class_number, class_number))
    rows = cur.fetchall()
    cur.close()

    return jsonify([{"id": row[0], "title": row[1]} for row in rows])
