from flask import Blueprint, render_template, session, redirect, url_for

parent_bp = Blueprint('parent', __name__)

@parent_bp.route('/parent')
def parent_dashboard():
    if session.get('role') != 'parent':
        return redirect(url_for('auth.login'))
    return render_template('parent/parent_dashboard.html')
