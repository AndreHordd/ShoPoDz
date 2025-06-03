from flask import Blueprint, request, jsonify
from app.utils.db import get_db

lesson_bp = Blueprint('lesson', __name__)

@lesson_bp.route('/api/lessons/create', methods=['POST'])
def create_lessons():
    class_id = request.form.get("class_id")
    if not class_id:
        return jsonify({"success": False, "error": "class_id is required"}), 400

    lessons = []
    for day in range(5):
        for num in range(1, 8):
            field = f"day_{day}_lesson_{num}"
            subject_id = request.form.get(field)
            if subject_id and subject_id.strip().isdigit():
                lessons.append((class_id, subject_id, day, num))

    conn = get_db()
    cur = conn.cursor()

    for cls_id, subj_id, day, order in lessons:
        cur.execute("""
            INSERT INTO lessons (class_id, subject_id, teacher_id, room_id, day, start_time, end_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (cls_id, subj_id, 2, 1, day, '08:00', '08:45'))

    conn.commit()
    cur.close()
    return jsonify({"success": True})


@lesson_bp.route('/api/lessons/<int:class_id>')
def get_lessons(class_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT l.day, l.subject_id, s.title
        FROM lessons l
        JOIN subjects s ON l.subject_id = s.subject_id
        WHERE l.class_id = %s
        ORDER BY l.day, l.lesson_id
    """, (class_id,))
    rows = cur.fetchall()
    cur.close()

    result = {}
    for day, _, title in rows:
        result.setdefault(day, []).append(title)
    return jsonify(result)
