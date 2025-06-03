from flask import Blueprint, request, jsonify
from app.utils.db import get_db

lesson_bp = Blueprint('lesson', __name__)

@lesson_bp.route('/api/lessons/create', methods=['POST'])
def create_lessons():
    class_id = request.form.get("class_id")

    if not class_id:
        return jsonify({"success": False, "error": "class_id is required"}), 400

    lessons = []
    for day_index in range(5):
        day = day_index + 1  # День з 1 по 5
        for lesson_num in range(1, 8):  # Урок з 1 по 7
            field = f"day_{day_index}_lesson_{lesson_num}"
            subject_id = request.form.get(field)
            if subject_id and subject_id.strip().isdigit():
                subj_id = int(subject_id)
                lessons.append((int(class_id), subj_id, day, lesson_num))

    # Мапа часу для уроків
    lesson_times = {
        1: ('08:00', '08:45'),
        2: ('08:55', '09:40'),
        3: ('09:50', '10:35'),
        4: ('10:45', '11:30'),
        5: ('11:40', '12:25'),
        6: ('12:35', '13:20'),
        7: ('13:30', '14:15')
    }

    conn = get_db()
    cur = conn.cursor()

    for cls_id, subj_id, day, lesson_num in lessons:
        start_time, end_time = lesson_times.get(lesson_num, ('08:00', '08:45'))
        cur.execute("""
            INSERT INTO lessons (class_id, subject_id, teacher_id, room_id, day, start_time, end_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (cls_id, subj_id, 2, 1, day, start_time, end_time))

    conn.commit()
    cur.close()
    return jsonify({"success": True})


@lesson_bp.route('/api/lessons/<int:class_id>')
def get_lessons(class_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT l.day, l.start_time, s.title
        FROM lessons l
        JOIN subjects s ON l.subject_id = s.subject_id
        WHERE l.class_id = %s
        ORDER BY l.day, l.start_time
    """, (class_id,))
    rows = cur.fetchall()
    cur.close()

    # Мапа часу на номер уроку
    def get_lesson_index_from_time(start_time):
        time_map = {
            '08:00:00': 1,
            '08:55:00': 2,
            '09:50:00': 3,
            '10:45:00': 4,
            '11:40:00': 5,
            '12:35:00': 6,
            '13:30:00': 7
        }
        return time_map.get(str(start_time))

    result = {i: {} for i in range(1, 6)}  # Пн–Пт

    for day, start_time, subject in rows:
        lesson_index = get_lesson_index_from_time(start_time)
        if lesson_index:
            result[day][lesson_index] = subject

    return jsonify(result)
