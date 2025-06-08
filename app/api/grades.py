# app/api/grades.py

from flask import (
    Blueprint, render_template,
    session, redirect, url_for,
    request, jsonify
)
from datetime import date, timedelta, datetime
from app.dao.grades_dao import (
    get_teacher_grades_week,
    get_students_in_class,
    add_or_update_grade
)

grade_bp = Blueprint('grade', __name__)

@grade_bp.route('/teacher/grades')
def teacher_grades():
    if session.get('role') != 'teacher':
        return redirect(url_for('auth.login'))

    tid = session['user_id']
    ws  = request.args.get('week_start')
    if ws:
        try:
            week_start = datetime.fromisoformat(ws).date()
        except ValueError:
            week_start = date.today() - timedelta(days=date.today().weekday())
    else:
        week_start = date.today() - timedelta(days=date.today().weekday())
    week_end = week_start + timedelta(days=6)

    data = get_teacher_grades_week(tid, week_start)
    return render_template(
        'teacher/grades.html',
        grades_data=data,
        week_start=week_start,
        week_end=week_end
    )

@grade_bp.route('/teacher/grades/students')
def fetch_students():
    class_id = request.args.get('class_id', type=int)
    if not class_id:
        return jsonify([])
    students = get_students_in_class(class_id)
    return jsonify([
        {'id': s.user_id,
         'name': f"{s.last_name} {s.first_name}"}
        for s in students
    ])

@grade_bp.route('/teacher/grades/add', methods=['POST'])
def add_grade_api():
    if session.get('role') != 'teacher':
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json() or {}
    les = data.get('lesson_id')
    stu = data.get('student_id')
    val = data.get('value')
    com = data.get('comment','').strip()

    g = add_or_update_grade(
        lesson_id=les,
        student_id=stu,
        teacher_id=session['user_id'],
        value=val,
        comment=com or None
    )
    return jsonify({'grade_id': g.grade_id}), 200
