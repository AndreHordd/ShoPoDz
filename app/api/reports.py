from flask import Blueprint, request, jsonify, make_response
from app.utils.db import get_db
import csv
import io
import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4

report_bp = Blueprint('report', __name__, url_prefix='/api/reports')

# Підключення кириличного шрифту
FONT_PATH = os.path.join(os.path.dirname(__file__), '../../static/fonts/DejaVuSans.ttf')
pdfmetrics.registerFont(TTFont("DejaVu", FONT_PATH))

DAY_NAMES = {
    1: "Понеділок",
    2: "Вівторок",
    3: "Середа",
    4: "Четвер",
    5: "П’ятниця"
}

@report_bp.route('/schedule/<int:class_id>')
def schedule_report(class_id):
    format = request.args.get('format', 'csv')
    conn = get_db()
    cur = conn.cursor()

    # Отримати назву класу
    cur.execute("SELECT class_number, subclass FROM classes WHERE class_id = %s", (class_id,))
    class_row = cur.fetchone()
    if not class_row:
        return jsonify({"error": "Клас не знайдено"}), 404
    class_name = f"{class_row[0]}-{class_row[1]}" if class_row[1] else str(class_row[0])

    # Розклад
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
        ORDER BY l.day, l.start_time;
    """, (class_id,))
    rows = cur.fetchall()

    if format == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['День', 'Час', 'Предмет', 'Вчитель', 'Кабінет'])
        for row in rows:
            writer.writerow([DAY_NAMES.get(row[0], row[0]), *row[1:]])

        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = f'attachment; filename=schedule_class_{class_name}.csv'
        response.headers['Content-Type'] = 'text/csv'
        return response

    elif format == 'pdf':
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        pdf.setFont("DejaVu", 12)
        width, height = A4

        x_start = 50
        y = height - 50
        row_height = 20

        pdf.drawString(x_start, y, f"Розклад для класу {class_name}")
        y -= row_height * 2

        pdf.setFont("DejaVu", 10)
        current_day = None

        for row in rows:
            day, time, subject, teacher, room = row
            if current_day != day:
                pdf.setFont("DejaVu", 10)
                pdf.drawString(x_start, y, f"{DAY_NAMES.get(day, day)}:")
                y -= row_height
                current_day = day

            line = f"{time} - {subject} ({teacher}) каб. {room}"
            pdf.drawString(x_start + 20, y, line)
            y -= row_height

            if y < 50:
                pdf.showPage()
                pdf.setFont("DejaVu", 10)
                y = height - 50

        pdf.save()
        buffer.seek(0)
        response = make_response(buffer.read())
        response.headers['Content-Disposition'] = f'inline; filename=schedule_class_{class_name}.pdf'
        response.headers['Content-Type'] = 'application/pdf'
        return response

    return jsonify({"error": "Invalid format"}), 400
