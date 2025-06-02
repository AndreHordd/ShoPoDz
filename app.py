from flask import Flask, session, redirect, url_for
from app.config import Config
from app.models import db
from app.api.auth import auth_bp
from app.api.teachers import teacher_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ініціалізація бази
    db.init_app(app)

    # Реєстрація маршрутів
    app.register_blueprint(auth_bp)
    app.register_blueprint(teacher_bp)

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
            return '👑 Панель адміністратора (заглушка)'
        elif role == 'student':
            return '🎓 Панель учня (заглушка)'
        elif role == 'parent':
            return '👪 Панель батьків (заглушка)'
        else:
            return '❌ Невідома роль'

    return app

# Для запуску напряму
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
