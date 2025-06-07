from flask import Blueprint, render_template, session, redirect, url_for, request
from datetime import date, timedelta, datetime
from app.dao.homework_dao import get_teacher_homework_week

homework_bp = Blueprint('homework', __name__)

@homework_bp.route('/teacher/homework')
def teacher_homework():
    # Захист від неавторизованих і не-вчителів
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('auth.login'))

    teacher_id = session['user_id']

    # Формування дати початку тижня
    week_start_str = request.args.get('week_start')
    if week_start_str:
        try:
            week_start = datetime.strptime(week_start_str, '%Y-%m-%d').date()
        except ValueError:
            week_start = date.today() - timedelta(days=date.today().weekday())
    else:
        week_start = date.today() - timedelta(days=date.today().weekday())

    # Кінець тижня для виводу у шаблон
    week_end = week_start + timedelta(days=6)
    # Поточна дата для контролю кнопок
    current_date = date.today()

    # Дістаємо домашки з DAO (групування по класах роби вже у шаблоні)
    homework_data = get_teacher_homework_week(teacher_id, week_start)

    return render_template(
        'teacher/homework.html',
        homework_data=homework_data,
        week_start=week_start,
        week_end=week_end,
        current_date=current_date
    )
