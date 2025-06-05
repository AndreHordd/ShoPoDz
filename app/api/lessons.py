from flask import Blueprint, request, jsonify
from app.utils.db import get_db

lesson_bp = Blueprint('lesson', __name__)

@lesson_bp.route('/api/lessons/create', methods=['POST'])
@lesson_bp.route('/api/lessons/create', methods=['POST'])
def create_lessons():
    class_id = request.form.get("class_id")
    if not class_id:
        return jsonify({"success": False, "error": "class_id is required"}), 400

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

    lessons = []
    for day_index in range(5):
        day = day_index + 1  # День з 1 по 5
        for lesson_num in range(1, 8):  # Урок з 1 по 7
            subject_field = f"day_{day_index}_lesson_{lesson_num}"
            teacher_field = f"teacher_day_{day_index}_lesson_{lesson_num}"
            room_field = f"room_day_{day_index}_lesson_{lesson_num}"

            subject_id = request.form.get(subject_field)
            teacher_id = request.form.get(teacher_field)
            room_id = request.form.get(room_field)

            if subject_id and subject_id.strip().isdigit():
                subj_id = int(subject_id)
                teacher = int(teacher_id) if teacher_id and teacher_id.isdigit() else None
                room = int(room_id) if room_id and room_id.isdigit() else None
                start_time, end_time = lesson_times.get(lesson_num, ('08:00', '08:45'))
                lessons.append((int(class_id), subj_id, teacher, room, day, start_time, end_time))

    conn = get_db()
    cur = conn.cursor()

    # Видалити старі, якщо існують — для редагування
    cur.execute("DELETE FROM lessons WHERE class_id = %s", (class_id,))

    for row in lessons:
        cur.execute("""
            INSERT INTO lessons (class_id, subject_id, teacher_id, room_id, day, start_time, end_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, row)

    conn.commit()
    cur.close()
    return jsonify({"success": True})


@lesson_bp.route('/api/lessons/<int:class_id>')
def get_lessons(class_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT l.day, l.start_time, s.title, t.first_name, t.last_name, r.room_number
        FROM lessons l
        JOIN subjects s ON l.subject_id = s.subject_id
        LEFT JOIN teachers t ON l.teacher_id = t.user_id
        LEFT JOIN rooms r ON l.room_id = r.room_id
        WHERE l.class_id = %s
        ORDER BY l.day, l.start_time
    """, (class_id,))
    rows = cur.fetchall()
    cur.close()

    def get_lesson_index_from_time(start_time):
        time_map = {
            '08:00:00': 1, '08:55:00': 2, '09:50:00': 3,
            '10:45:00': 4, '11:40:00': 5, '12:35:00': 6, '13:30:00': 7
        }
        return time_map.get(str(start_time))

    result = {i: {} for i in range(1, 6)}

    for day, start_time, subject, teacher_name, teacher_surname, room_number in rows:
        lesson_index = get_lesson_index_from_time(start_time)
        if lesson_index:
            teacher = f"{teacher_name} {teacher_surname}" if teacher_name else ""
            room = f"({room_number})" if room_number else ""
            result[day][lesson_index] = f"{subject}<br><small>{teacher} {room}</small>"

    return jsonify(result)

@lesson_bp.route('/api/lessons/delete/<int:class_id>', methods=['DELETE'])
def delete_schedule(class_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM lessons WHERE class_id = %s", (class_id,))
    conn.commit()
    cur.close()
    return jsonify({"success": True})

@lesson_bp.route('/api/lessons/full/<int:class_id>')
def get_full_schedule(class_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT day, start_time, subject_id, teacher_id, room_id
        FROM lessons
        WHERE class_id = %s
    """, (class_id,))
    rows = cur.fetchall()
    cur.close()

    time_to_index = {
        '08:00:00': 1, '08:55:00': 2, '09:50:00': 3,
        '10:45:00': 4, '11:40:00': 5, '12:35:00': 6,
        '13:30:00': 7
    }

    result = {}
    for day, start_time, subject_id, teacher_id, room_id in rows:
        index = time_to_index.get(str(start_time))
        if index:
            key = f"{day}_{index}"
            result[key] = {
                "subject_id": subject_id,
                "teacher_id": teacher_id,
                "room_id": room_id
            }

    return jsonify(result)
