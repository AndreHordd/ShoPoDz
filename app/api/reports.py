from flask import Blueprint, request, render_template
from app.utils.db import get_db

report_bp = Blueprint('report', __name__, url_prefix='/api/reports')


@report_bp.route('/schedule/preview/<int:class_id>')
def schedule_preview(class_id):
    conn = get_db()
    cur = conn.cursor()

    # Отримати назву класу
    cur.execute("""
        SELECT class_number, subclass
        FROM classes
        WHERE class_id = %s
    """, (class_id,))
    row = cur.fetchone()
    if not row:
        return "Клас не знайдено", 404

    class_name = f"{row[0]}-{row[1]}"

    # Отримати всі записи розкладу
    cur.execute("""
        SELECT 
            l.day,
            l.start_time,
            s.title AS subject_title,
            CONCAT(t.last_name, ' ', t.first_name, ' ', COALESCE(t.middle_name, '')) AS teacher_name,
            r.room_number
        FROM lessons l
        JOIN subjects s ON l.subject_id = s.subject_id
        JOIN teachers t ON l.teacher_id = t.user_id
        JOIN rooms r ON l.room_id = r.room_id
        WHERE l.class_id = %s
        ORDER BY l.start_time, l.day
    """, (class_id,))
    rows = cur.fetchall()

    # Динамічно створюємо унікальні start_time
    unique_times = sorted(set(row[1] for row in rows))
    schedule = {time: {day: None for day in range(1, 6)} for time in unique_times}

    for day, time, subject, teacher, room in rows:
        schedule[time][day] = {
            'subject': subject,
            'teacher': teacher,
            'room': room
        }

    return render_template("admin/schedule_report.html", class_name=class_name, schedule=schedule)
