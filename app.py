from flask import Flask, session, redirect, url_for

from app.api.admin import admin_bp
from app.api.students import student_bp
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

    return app

# Для запуску напряму
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
