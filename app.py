from flask import Flask, session, redirect, url_for

from app.config import Config
from app.models import db
from app.api.auth import auth_bp
from app.api.teachers import teacher_bp
from app.api.admin import admin_bp
from app.api.students import student_bp
from app.api.parents import parent_bp
from app.api.classes import class_bp
from app.api.subjects import subject_bp
from app.api.lessons import lesson_bp
from app.api.rooms import room_bp
from app.api.announcements import announcement_bp
from flask import Flask, session, redirect, url_for, render_template  # ← + render_template
from app.dao.lessons_dao import get_teacher_schedule                 # ← + ця функція
from app.api.homework import homework_bp
from datetime import timedelta
from app.api.grades import grade_bp


def add_days(date_obj, days):
    return date_obj + timedelta(days=days)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ініціалізація бази
    db.init_app(app)

    # Реєстрація маршрутів
    app.register_blueprint(auth_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(parent_bp)
    app.register_blueprint(class_bp)
    app.register_blueprint(subject_bp)
    app.register_blueprint(lesson_bp)
    app.register_blueprint(room_bp)
    app.register_blueprint(announcement_bp)
    app.register_blueprint(homework_bp)
    app.register_blueprint(grade_bp)

    # ----------- /teacher/schedule -----------------
    @app.route('/teacher/schedule')
    def teacher_schedule():
        # перевірка логіну й ролі
        if 'user_id' not in session or session.get('role') != 'teacher':
            return redirect(url_for('auth.login'))

        lessons = get_teacher_schedule(session['user_id'])
        return render_template('teacher/schedule.html', lessons=lessons)


    # Головна сторінка → форма авторизації
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    # Перенаправлення після входу за роллю
    @app.route('/redirect-by-role')
    def redirect_by_role():
        if 'user_id' not in session or 'role' not in session:
            return redirect(url_for('auth.login'))

        role = session['role']

        if role == 'teacher':
            return redirect(url_for('teacher.dashboard'))
        elif role == 'admin':
            return redirect(url_for('admin.admin_dashboard'))
        elif role == 'student':
            return redirect(url_for('student.student_dashboard'))
        elif role == 'parent':
            return redirect(url_for('parent.parent_dashboard'))
        else:
            return '❌ Невідома роль'

    app.jinja_env.filters['add_days'] = add_days
    return app

# Для запуску напряму
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
