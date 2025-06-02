from flask import Blueprint, render_template, session, redirect, url_for

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
def admin_dashboard():
    # Перевірка ролі
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    return render_template('admin/admin_dashboard.html')
