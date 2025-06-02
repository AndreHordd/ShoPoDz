from flask import Blueprint, render_template, session, redirect, url_for
from app.dao.classes_dao import get_classes_by_teacher_id

teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher')

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
    return render_template('teacher/teacher_classes.html', classes=classes)
