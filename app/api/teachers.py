from flask import Blueprint, render_template, session, redirect, url_for

teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher')

@teacher_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('auth.login'))

    return render_template('teacher/dashboard.html', teacher_name="Вчитель")
