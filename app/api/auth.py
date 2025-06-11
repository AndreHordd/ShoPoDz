from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.services.user_service import get_user_by_email
from app.utils.auth_utils import verify_user_credentials
from app.utils.db import get_db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def get_children_by_parent(parent_id):
    """Повертає список дітей (user_id, first_name, last_name, class_id) для батька."""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT user_id, first_name, last_name, class_id FROM students WHERE parent_id = %s",
            (parent_id,)
        )
        return [
            {"user_id": row[0], "first_name": row[1], "last_name": row[2], "class_id": row[3]}
            for row in cur.fetchall()
        ]


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form['email']
        password = request.form['password']

        user = get_user_by_email(email)
        if user and verify_user_credentials(user, password):
            session['user_id']  = user.user_id
            session['role']     = user.role
            session['username'] = user.email

            # Батьківський профіль — вибір дитини
            if user.role == "parent":
                children = get_children_by_parent(user.user_id)
                if not children:
                    flash("Не знайдено дітей для вашого профілю.", "danger")
                    return render_template('auth/login.html')
                if len(children) == 1:
                    session['student_id'] = children[0]["user_id"]
                    # Привітання
                    flash(f"Вітаємо, {children[0]['first_name']}!", "welcome")
                    print("✅ Успішний вхід (parent, 1 child):", user.email)
                    return redirect(url_for('parent.parent_dashboard'))
                else:
                    session['children'] = children
                    print("✅ Вхід, кілька дітей:", [c['first_name'] for c in children])
                    return redirect(url_for('parent.choose_child'))

            print("✅ Успішний вхід:", user.email, user.role)
            return redirect(url_for('redirect_by_role'))
        else:
            print("❌ Авторизація не пройшла:", email)
            flash('Невірна пошта або пароль', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('👋 Ви вийшли із системи', 'info')
    return redirect(url_for('auth.login'))
