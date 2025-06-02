from flask import Flask, session, redirect, url_for
from app.config import Config
from app.models import db
from app.api.auth import auth_bp  # Імпортуємо після ініціалізації app

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Реєстрація blueprint'а для /auth
app.register_blueprint(auth_bp)

@app.route('/')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return f"Привіт, ваш ID: {session['user_id']} (роль: {session['role']})"

if __name__ == '__main__':
    app.run(debug=True)
