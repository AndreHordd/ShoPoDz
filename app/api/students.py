from flask import Blueprint, render_template, session, redirect, url_for

student_bp = Blueprint('student', __name__)

@student_bp.route('/student')
def student_dashboard():
    if session.get('role') != 'student':
        return redirect(url_for('auth.login'))
    return render_template('student/student_dashboard.html')
