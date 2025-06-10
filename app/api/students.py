from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify

from app.models import Student
from app.utils.db import get_db

student_bp = Blueprint('student', __name__)

@student_bp.route('/student')
def student_dashboard():
    if session.get('role') != 'student':
        return redirect(url_for('auth.login'))
    return render_template('student/student_dashboard.html')

def get_students_for_class(class_id):
    return  Student.query.filter_by(class_id=class_id).order_by(Student.last_name.asc()).all()

@student_bp.route('/api/students', methods=['GET'])
def get_students():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.user_id, s.first_name, s.last_name, s.middle_name,
               s.class_id, s.parent_id,
               CONCAT(c.class_number, '-', c.subclass) AS class_name,
               c.subclass
        FROM students s
        JOIN classes c ON s.class_id = c.class_id
    """)
    rows = cur.fetchall()
    cur.close()
    return jsonify([
        {
            "user_id": r[0],
            "first_name": r[1],
            "last_name": r[2],
            "middle_name": r[3],
            "class_id": r[4],
            "parent_id": r[5],
            "class": r[6],         # Назва класу (наприклад, 10-А)
            "subclass": r[7]       # Окремо літера класу (наприклад, А)
        } for r in rows
    ])

@student_bp.route('/api/students', methods=['POST'])
def add_student():
    data = request.get_json()
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    middle_name = data.get('middle_name') or ''
    class_id = data.get('class_id')

    if not first_name or not last_name or not class_id:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400

    conn = get_db()
    cur = conn.cursor()

    # 1. Додаємо користувача до таблиці users
    cur.execute("""
        INSERT INTO users (email, password_hash, role)
        VALUES (%s, %s, 'student')
        RETURNING user_id
    """, (f"student.{first_name.lower()}_{last_name.lower()}@school.com", 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f'))  # або замініть логікою генерації
    user_id = cur.fetchone()[0]

    # 2. Додаємо запис у students
    cur.execute("""
        INSERT INTO students (user_id, first_name, last_name, middle_name, class_id)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, first_name, last_name, middle_name, class_id))

    conn.commit()
    cur.close()

    return jsonify({'success': True})

@student_bp.route('/api/students/<int:user_id>', methods=['PUT'])
def update_student(user_id):
    data = request.get_json()
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    middle_name = data.get('middle_name') or ''
    class_id = data.get('class_id')
    parent_id = data.get('parent_id')

    email = f"student.{first_name.lower()}_{last_name.lower()}@school.com"

    conn = get_db()
    cur = conn.cursor()

    # Оновити таблицю users
    cur.execute("UPDATE users SET email = %s WHERE user_id = %s", (email, user_id))

    # Оновити таблицю students
    cur.execute("""
        UPDATE students
        SET first_name = %s, last_name = %s, middle_name = %s, class_id = %s, parent_id = %s
        WHERE user_id = %s
    """, (first_name, last_name, middle_name, class_id, parent_id, user_id))

    conn.commit()
    cur.close()
    return jsonify({"success": True})

@student_bp.route('/api/students/<int:user_id>', methods=['GET'])
def get_single_student(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.user_id, s.first_name, s.last_name, s.middle_name,
               s.class_id, s.parent_id, u.email,
               CONCAT(c.class_number, '-', c.subclass) AS class_name
        FROM students s
        JOIN users u ON s.user_id = u.user_id
        JOIN classes c ON s.class_id = c.class_id
        WHERE s.user_id = %s
    """, (user_id,))
    row = cur.fetchone()
    cur.close()
    if row:
        return jsonify({
            "user_id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "middle_name": row[3],
            "class_id": row[4],
            "parent_id": row[5],
            "email": row[6],
            "class": row[7]  # назва класу для виводу
        })
    else:
        return jsonify({"error": "Student not found"}), 404

@student_bp.route('/api/students/<int:user_id>', methods=['DELETE'])
def delete_student(user_id):
    conn = get_db()
    cur = conn.cursor()

    # Видаляємо студента
    cur.execute("DELETE FROM students WHERE user_id = %s", (user_id,))

    # Видаляємо пов'язаний запис з users
    cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))

    conn.commit()
    cur.close()
    return jsonify({"success": True})
