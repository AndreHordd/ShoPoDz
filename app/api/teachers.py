from flask import Blueprint, render_template, session, redirect, url_for
from app.dao.classes_dao import get_classes_by_teacher_id
from app.services.class_service import get_students_by_class_id

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

    # Додай до кожного класу його учнів
    for cls in classes:
        cls.students = get_students_by_class_id(cls.class_id)

    return render_template('teacher/teacher_classes.html', classes=classes)

@teacher_bp.route('/class/<int:class_id>/students')
def students_by_class(class_id):
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('auth.login'))

    students = get_students_by_class_id(class_id)
    return render_template('teacher/teacher_students.html', students=students)