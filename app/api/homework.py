# app/api/homework.py

from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from datetime import date, datetime, timedelta
from app.dao.homework_dao import (
    get_teacher_homework_week,
    add_homework,
    update_homework,
    delete_homework
)

homework_bp = Blueprint(
    'homework',
    __name__,
    url_prefix='/teacher/homework'
)

@homework_bp.route('', methods=['GET'])
def teacher_homework():
    # доступ лише для вчителів
    if session.get('role') != 'teacher' or 'user_id' not in session:
        return redirect(url_for('auth.login'))

    teacher_id = session['user_id']

    # обчислюємо понеділок тижня
    week_start_str = request.args.get('week_start')
    if week_start_str:
        try:
            week_start = datetime.strptime(week_start_str, '%Y-%m-%d').date()
        except ValueError:
            week_start = date.today() - timedelta(days=date.today().weekday())
    else:
        week_start = date.today() - timedelta(days=date.today().weekday())

    week_end     = week_start + timedelta(days=6)
    current_date = date.today()

    # отримуємо уроки + домашні завдання
    homework_data = get_teacher_homework_week(teacher_id, week_start)

    return render_template(
        'teacher/homework.html',
        homework_data=homework_data,
        week_start=week_start,
        week_end=week_end,
        current_date=current_date
    )

@homework_bp.route('/add', methods=['POST'])
def add_hw():
    if session.get('role') != 'teacher':
        return jsonify(error="Forbidden"), 403

    data = request.get_json() or {}
    lesson_id   = data.get('lesson_id')
    description = data.get('description', '')
    deadline    = data.get('deadline')

    success, result = add_homework(lesson_id, description, deadline)
    if not success:
        return jsonify(error=result), 400

    hw = result
    return jsonify({
        "homework_id": hw.homework_id,
        "lesson_id":   hw.lesson_id,
        "description": hw.description,
        "deadline":    hw.deadline.isoformat()
    }), 201

@homework_bp.route('/<int:hw_id>', methods=['PUT'])
def edit_hw(hw_id):
    if session.get('role') != 'teacher':
        return jsonify(error="Forbidden"), 403

    data = request.get_json() or {}
    description = data.get('description', '')
    deadline    = data.get('deadline')

    success, result = update_homework(hw_id, description, deadline)
    if not success:
        return jsonify(error=result), 400

    hw = result
    return jsonify({
        "homework_id": hw.homework_id,
        "description": hw.description,
        "deadline":    hw.deadline.isoformat()
    })

@homework_bp.route('/<int:hw_id>', methods=['DELETE'])
def del_hw(hw_id):
    if session.get('role') != 'teacher':
        return jsonify(error="Forbidden"), 403

    success, result = delete_homework(hw_id)
    if not success:
        return jsonify(error=result), 400

    return jsonify(success=True)
