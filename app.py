from flask import Flask, session, redirect, url_for
from app.models import db
from app.api.auth import auth_bp

app = Flask(__name__)
app.secret_key = 'your-very-secret-key'  # ЗАМІНИ на секретний ключ

# Конфігурація БД
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:yourpassword@localhost/yourdbname'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.register_blueprint(auth_bp)

@app.route('/')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return f"Привіт, ваш ID: {session['user_id']} (роль: {session['role']})"


if __name__ == '__main__':
    app.run(debug=True)
