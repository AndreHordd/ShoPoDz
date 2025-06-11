from flask import Blueprint, jsonify, render_template, session, redirect, url_for, request
from app.dao.student_portal_dao import StudentPortalDAO

student_portal_bp = Blueprint("student_portal", __name__, url_prefix="/student")


def _only_student():
    return session.get("role") == "student" and "user_id" in session


@student_portal_bp.route("/")
def dashboard():
    return (
        render_template("student/student_dashboard.html")
        if _only_student()
        else redirect(url_for("auth.login"))
    )


# ---------- API ----------
@student_portal_bp.route("/api/profile")
def profile_api():
    if not _only_student():
        return jsonify(error="forbidden"), 403
    profile_data = StudentPortalDAO.profile(session["user_id"])
    if not profile_data:
        return jsonify(error="student not found"), 404
    return jsonify(profile_data)


@student_portal_bp.route("/api/schedule")
def schedule_api():
    if not _only_student():
        return jsonify(error="forbidden"), 403
    return jsonify(StudentPortalDAO.schedule(session["user_id"]))


@student_portal_bp.route("/api/homework")
def homework_api():
    if not _only_student():
        return jsonify(error="forbidden"), 403
    return jsonify(StudentPortalDAO.homework_list(session["user_id"]))


@student_portal_bp.route("/api/homework/<int:hw_id>/toggle", methods=["POST"])
def toggle_homework(hw_id):
    if not _only_student():
        return jsonify(error="forbidden"), 403
    ok = StudentPortalDAO.toggle_done(session["user_id"], hw_id)
    return jsonify(done=ok)


@student_portal_bp.route("/api/attendance")
def attendance_api():
    if not _only_student():
        return jsonify(error="forbidden"), 403
    return jsonify(StudentPortalDAO.attendance(session["user_id"]))


@student_portal_bp.route("/api/teachers")
def teachers_api():
    if not _only_student():
        return jsonify(error="forbidden"), 403
    return jsonify(StudentPortalDAO.teachers_and_rooms(session["user_id"]))


@student_portal_bp.route("/api/announcements")
def announcements_api():
    if not _only_student():
        return jsonify(error="forbidden"), 403
    return jsonify(StudentPortalDAO.announcements())
