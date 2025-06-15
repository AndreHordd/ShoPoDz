from flask import Blueprint, request, jsonify
from app.utils.db import get_db

lesson_bp = Blueprint('lesson', __name__)

@lesson_bp.route('/api/lessons/create', methods=['POST'])
def create_lessons():
    class_id = request.form.get("class_id")
    if not class_id:
        return jsonify({"success": False, "error": "class_id is required"}), 400

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
        day = day_index + 1
        for lesson_num in range(1, 8):
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

    # 🧹 Очистити старі дані цього класу
    cur.execute("DELETE FROM lessons WHERE class_id = %s", (class_id,))

    for row in lessons:
        class_id, subject_id, teacher_id, room_id, day, start_time, end_time = row

        if teacher_id:
            cur.execute("""
                SELECT t.last_name, t.first_name, t.middle_name,
                       c.class_number, c.subclass
                FROM lessons l
                JOIN teachers t ON t.user_id = l.teacher_id
                JOIN classes c ON l.class_id = c.class_id
                WHERE l.teacher_id = %s AND l.day = %s AND l.start_time = %s AND l.class_id != %s
            """, (teacher_id, day, start_time, class_id))
            conflict = cur.fetchone()

            if conflict:
                last_name, first_name, middle_name, class_number, subclass = conflict
                teacher_name = f"{last_name} {first_name} {middle_name or ''}".strip()
                class_name = f"{class_number}-{subclass}"

                day_names = {
                    1: 'Понеділок',
                    2: 'Вівторок',
                    3: 'Середа',
                    4: 'Четвер',
                    5: 'П’ятниця'
                }

                time_label = start_time[:5]
                day_label = day_names.get(day, f"день {day}")

                return jsonify({
                    "success": False,
                    "error": f"❗ {teacher_name} вже має урок у {class_name} в {day_label} о {time_label}. Змініть розклад."
                }), 400

        # ✅ Вставка уроку
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
