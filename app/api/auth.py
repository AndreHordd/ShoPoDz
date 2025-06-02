from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from app.utils.auth_utils import verify_user_credentials
from app.services.user_service import get_user_by_email

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = get_user_by_email(email)
        if user and verify_user_credentials(user, password):
            session['user_id'] = user.id
            session['role'] = user.role
            flash('Успішний вхід', 'success')
            return redirect(url_for('dashboard'))  # змінити на твій реальний маршрут
        else:
            flash('Невірний email або пароль', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Вихід виконано', 'info')
    return redirect(url_for('auth.login'))
