from flask import Blueprint, render_template, session, redirect, url_for

student_bp = Blueprint('student', __name__)

@student_bp.route('/student')
def student_dashboard():
    if session.get('role') != 'student':
        return redirect(url_for('auth.login'))
    return render_template('student/student_dashboard.html')

def get_students_for_class(class_id):
    return Student.query.filter_by(class_id=class_id).order_by(Student.last_name.asc()).all()
