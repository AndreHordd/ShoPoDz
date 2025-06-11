from flask import Blueprint, request, jsonify
from app.utils.db import get_db
from psycopg2 import errors

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

# 🔹 Отримати всі предмети
@subject_bp.route("/api/subjects", methods=["GET"])
def get_subjects():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT subject_id, title, first_teaching_grade, last_teaching_grade FROM subjects ORDER BY title")
    rows = cur.fetchall()
    cur.close()
    return jsonify([
        {
            "subject_id": r[0],
            "title": r[1],
            "first_teaching_grade": r[2],
            "last_teaching_grade": r[3],
        } for r in rows
    ])


# 🔹 Додати новий предмет
@subject_bp.route("/api/subjects", methods=["POST"])
def add_subject():
    data = request.get_json()
    title = data.get("title")
    first = data.get("first_teaching_grade")
    last = data.get("last_teaching_grade")

    if not all([title, first, last]):
        return jsonify({"success": False, "error": "Усі поля обов'язкові"}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO subjects (title, first_teaching_grade, last_teaching_grade)
        VALUES (%s, %s, %s)
    """, (title, first, last))
    conn.commit()
    cur.close()
    return jsonify({"success": True})


# 🔹 Оновити предмет
@subject_bp.route("/api/subjects/<int:subject_id>", methods=["PUT"])
def update_subject(subject_id):
    data = request.get_json()
    title = data.get("title")
    first = data.get("first_teaching_grade")
    last = data.get("last_teaching_grade")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE subjects
        SET title = %s,
            first_teaching_grade = %s,
            last_teaching_grade = %s
        WHERE subject_id = %s
    """, (title, first, last, subject_id))
    conn.commit()
    cur.close()
    return jsonify({"success": True})


@subject_bp.route('/api/subjects/<int:subject_id>', methods=['DELETE'])
def delete_subject(subject_id):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM subjects WHERE subject_id = %s", (subject_id,))
        conn.commit()
        return jsonify({"success": True})
    except errors.ForeignKeyViolation:
        conn.rollback()
        return jsonify({"success": False, "error": "Неможливо видалити предмет, бо він використовується у розкладі або викладачами."}), 400
    finally:
        cur.close()
