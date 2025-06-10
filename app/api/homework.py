# app/api/homework.py

from flask import (
    Blueprint, render_template, session,
    redirect, url_for, request, jsonify
)
from datetime import date, timedelta, datetime
from app.dao.homework_dao import (
    get_teacher_homework_week,
    add_homework,
    update_homework,
    delete_homework
)

homework_bp = Blueprint('homework', __name__)


@homework_bp.route('/teacher/homework')
def teacher_homework():
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('auth.login'))

    teacher_id = session['user_id']

    # Визначаємо понеділок тижня
    week_start_str = request.args.get('week_start')
    if week_start_str:
        try:
            week_start = datetime.fromisoformat(week_start_str).date()
        except ValueError:
            week_start = date.today() - timedelta(days=date.today().weekday())
    else:
        week_start = date.today() - timedelta(days=date.today().weekday())

    week_end     = week_start + timedelta(days=6)
    current_date = date.today()

    homework_data = get_teacher_homework_week(teacher_id, week_start)

    return render_template(
        'teacher/homework.html',
        homework_data=homework_data,
        week_start=week_start,
        week_end=week_end,
        current_date=current_date
    )

@homework_bp.route('/teacher/homework/add', methods=['POST'])
def add_homework_api():
    if 'user_id' not in session or session.get('role') != 'teacher':
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json() or {}
    teacher_id  = session['user_id']
    class_id    = data.get('class_id')
    subject_id  = data.get('subject_id')
    description = data.get('description')
    deadline    = data.get('deadline')

    if not (class_id and subject_id and description and deadline):
        return jsonify({'error': 'Заповніть всі поля'}), 400

    success, result = add_homework(teacher_id, class_id, subject_id, description, deadline)
    if success:
        return jsonify({'homework_id': result.homework_id}), 200
    return jsonify({'error': result}), 400

@homework_bp.route('/teacher/homework/<int:homework_id>', methods=['PUT'])
def update_homework_api(homework_id):
    if 'user_id' not in session or session.get('role') != 'teacher':
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json() or {}
    description = data.get('description')
    deadline    = data.get('deadline')

    success, result = update_homework(homework_id, description, deadline)
    if success:
        return jsonify({'homework_id': result.homework_id}), 200
    return jsonify({'error': result}), 400


@homework_bp.route('/teacher/homework/<int:homework_id>', methods=['DELETE'])
def delete_homework_api(homework_id):
    if 'user_id' not in session or session.get('role') != 'teacher':
        return jsonify({'error': 'Unauthorized'}), 401

    success, result = delete_homework(homework_id)
    if success:
        return jsonify({'message': 'Deleted'}), 200
    return jsonify({'error': result}), 400
