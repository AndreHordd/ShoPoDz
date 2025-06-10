from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
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
        {'id': s.user_id, 'name': f"{s.last_name} {s.first_name}"}
        for s in students
    ])

@grade_bp.route('/teacher/grades/add', methods=['POST'])
def add_grade_api():
    if session.get('role') != 'teacher':
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.get_json() or {}
    lesson_id = data.get('lesson_id')
    student_id = data.get('student_id')
    value = data.get('value')
    comment = data.get('comment', '').strip()
    grade_date = data.get('date')  # дата у форматі 'YYYY-MM-DD'

    if not all([lesson_id, student_id, value, grade_date]):
        return jsonify({'error': 'Missing fields'}), 400

    g = add_or_update_grade(
        lesson_id=lesson_id,
        student_id=student_id,
        teacher_id=session['user_id'],
        value=value,
        grade_date=grade_date,
        comment=comment or None
    )
    return jsonify({'grade_id': g.grade_id}), 200

@grade_bp.route('/teacher/grades/existing')
def fetch_existing_grades():
    lesson_id = request.args.get('lesson_id', type=int)
    grade_date = request.args.get('date')
    from app.models import LessonSession, Grade
    # Знаходимо session (якщо є)
    session = LessonSession.query.filter_by(lesson_id=lesson_id, session_date=grade_date).first()
    if not session:
        return jsonify([])
    grades = Grade.query.filter_by(session_id=session.session_id).all()
    return jsonify([
        {
            'student_id': g.student_id,
            'grade_value': g.grade_value,
            'comment': g.comment or ''
        } for g in grades
    ])
