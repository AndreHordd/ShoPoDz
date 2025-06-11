from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from app.dao.classes_dao import get_classes_by_teacher_id
from app.services.class_service import get_students_by_class_id
from app.utils.db import get_db
from app.api.transliteration import transliterate
import hashlib

teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher')
api_teacher_bp = Blueprint('api_teacher', __name__, url_prefix='/api')

def hash_password(plain_password):
    return hashlib.sha256(plain_password.encode()).hexdigest()

@teacher_bp.route('/dashboard')
def dashboard():
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('auth.login'))
    return render_template('teacher/dashboard.html', teacher_name=session.get('username', 'Вчитель'))

@teacher_bp.route('/classes')
def classes():
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('auth.login'))

    teacher_id = session.get('user_id')
    classes = get_classes_by_teacher_id(teacher_id)

    for cls in classes:
        cls.students = get_students_by_class_id(cls.class_id)

    return render_template('teacher/teacher_classes.html', classes=classes)

@teacher_bp.route('/class/<int:class_id>/students')
def students_by_class(class_id):
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('auth.login'))

    students = get_students_by_class_id(class_id)
    return render_template('teacher/teacher_students.html', students=students)

# ---------- API HANDLERS ----------

def get_teachers():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT t.user_id, t.first_name, t.last_name, t.middle_name,
               t.salary, t.birth_date, t.hire_date,
               ARRAY(
                   SELECT ts.subject_id FROM teacher_subjects ts
                   WHERE ts.teacher_id = t.user_id
               ) AS subject_ids
        FROM teachers t
        ORDER BY t.last_name
    """)
    teachers = cur.fetchall()
    cur.close()

    return jsonify([
        {
            "user_id": t[0],
            "first_name": t[1],
            "last_name": t[2],
            "middle_name": t[3],
            "salary": float(t[4]),
            "birth_date": t[5].isoformat(),
            "hire_date": t[6].isoformat(),
            "subject_ids": t[7]
        }
        for t in teachers
    ])

def add_teacher():
    data = request.get_json()
    first = data.get("first_name")
    last = data.get("last_name")
    middle = data.get("middle_name") or ''
    salary = data.get("salary")
    birth = data.get("birth_date")
    hire = data.get("hire_date")
    subject_ids = data.get("subject_ids", [])

    if not all([first, last, salary, birth, hire]):
        return jsonify({"success": False, "error": "Всі поля обов'язкові"}), 400

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users (email, password_hash, role)
        VALUES (%s, %s, 'teacher')
        RETURNING user_id
    """, ("temp@school.com", "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f"))
    user_id = cur.fetchone()[0]

    first_latin = transliterate(first.lower())
    last_latin = transliterate(last.lower())
    email = f"t{user_id}.{first_latin}_{last_latin}@school.com"
    password = f"s{user_id}.{first_latin[0]}{last_latin[0]}"
    hashed = hash_password(password)

    cur.execute("UPDATE users SET email = %s, password_hash = %s WHERE user_id = %s", (email, hashed, user_id))
    cur.execute("""
        INSERT INTO teachers (user_id, first_name, last_name, middle_name, salary, birth_date, hire_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (user_id, first, last, middle, salary, birth, hire))

    for subject_id in subject_ids:
        cur.execute("INSERT INTO teacher_subjects (teacher_id, subject_id) VALUES (%s, %s)", (user_id, subject_id))

    conn.commit()
    cur.close()
    return jsonify({"success": True})

def update_teacher(user_id):
    data = request.get_json()
    first = data.get("first_name")
    last = data.get("last_name")
    middle = data.get("middle_name") or ''
    salary = data.get("salary")
    birth = data.get("birth_date")
    hire = data.get("hire_date")
    subject_ids = data.get("subject_ids", [])

    if not all([first, last, salary, birth, hire]):
        return jsonify({"success": False, "error": "Всі поля обов'язкові"}), 400

    first_lat = transliterate(first.lower())
    last_lat = transliterate(last.lower())
    email = f"t{user_id}.{first_lat}_{last_lat}@school.com"
    password = f"t{user_id}.{first_lat[0]}{last_lat[0]}"
    hashed_pw = hash_password(password)

    conn = get_db()
    cur = conn.cursor()

    cur.execute("UPDATE users SET email = %s, password_hash = %s WHERE user_id = %s", (email, hashed_pw, user_id))

    cur.execute("""
        UPDATE teachers
        SET first_name=%s, last_name=%s, middle_name=%s,
            salary=%s, birth_date=%s, hire_date=%s
        WHERE user_id = %s
    """, (first, last, middle, salary, birth, hire, user_id))

    cur.execute("DELETE FROM teacher_subjects WHERE teacher_id = %s", (user_id,))
    for subject_id in subject_ids:
        cur.execute("INSERT INTO teacher_subjects (teacher_id, subject_id) VALUES (%s, %s)", (user_id, subject_id))

    conn.commit()
    cur.close()
    return jsonify({"success": True})

def delete_teacher(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM teacher_subjects WHERE teacher_id = %s", (user_id,))
    cur.execute("DELETE FROM teachers WHERE user_id = %s", (user_id,))
    cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
    conn.commit()
    cur.close()
    return jsonify({"success": True})

# ---------- REGISTER API ROUTES ----------
api_teacher_bp.add_url_rule("/teachers", view_func=get_teachers, methods=["GET"])
api_teacher_bp.add_url_rule("/teachers", view_func=add_teacher, methods=["POST"])
api_teacher_bp.add_url_rule("/teachers/<int:user_id>", view_func=update_teacher, methods=["PUT"])
api_teacher_bp.add_url_rule("/teachers/<int:user_id>", view_func=delete_teacher, methods=["DELETE"])
