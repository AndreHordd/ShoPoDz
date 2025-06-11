# D:/Python/ShoPoDz/app.py
from datetime import timedelta

from flask import Flask, session, redirect, url_for, render_template   # + render_template
from app.config import Config
from app.models import db

from app.utils.db import init_db, close_db
from app.dao.lessons_dao import get_teacher_schedule                  # + ця функція

# ---------- blueprints ----------
from app.api.auth           import auth_bp
from app.api.teachers       import teacher_bp
from app.api.admin          import admin_bp
from app.api.students       import student_bp
from app.api.parents        import parent_bp
from app.api.classes        import class_bp
from app.api.subjects       import subject_bp
from app.api.lessons        import lesson_bp
from app.api.rooms          import room_bp
from app.api.announcements  import announcement_bp
from app.api.homework       import homework_bp
from app.api.grades         import grade_bp
from app.api.student_portal import student_portal_bp
from app.api.messages import messages_bp, api_bp as api_messenger_bp
from app.api.attendance import attendance_bp
from app.api.attendance import attendance_bp
from app.api.signatures import signatures_bp
# ---------------------------------------------------------------------------
def add_days(date_obj, days):
    return date_obj + timedelta(days=days)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()

    # blueprints
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
    app.register_blueprint(student_portal_bp)
    app.register_blueprint(signatures_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(api_messenger_bp)
    app.register_blueprint(attendance_bp)

    # -------------------- teacher schedule --------------------
    @app.route("/teacher/schedule")
    def teacher_schedule():
        if session.get("role") != "teacher":
            return redirect(url_for("auth.login"))
        lessons = get_teacher_schedule(session["user_id"])
        return render_template("teacher/schedule.html", lessons=lessons)
    # ----------------------------------------------------------

    @app.route("/")
    def index():
        return redirect(url_for("auth.login"))

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("auth.login"))

    @app.route("/redirect-by-role")
    def redirect_by_role():
        role = session.get("role")
        if role == "teacher":
            return redirect(url_for("teacher.dashboard"))
        if role == "admin":
            return redirect(url_for("admin.admin_dashboard"))
        if role == "student":
            return redirect(url_for("student_portal.dashboard"))
        if role == "parent":
            return redirect(url_for("parent.parent_dashboard"))
        return "❌ unknown role", 400

    app.jinja_env.filters["add_days"] = add_days
    return app


if __name__ == "__main__":
    create_app().run(debug=True)
