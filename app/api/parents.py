# app/api/parents.py
from datetime import date, timedelta, datetime
from sqlalchemy import and_, func
from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from sqlalchemy import func

from app.utils.db import get_db
from app.dao.students_dao import get_student_by_parent
from app.models import Lesson, Homework, Grade, Attendance

parent_bp = Blueprint("parent", __name__)

# ────────────────────────────────────────────────────────
#  ВНУТРІШНІ ФУНКЦІЇ ПІДПИСУ (без окремого DAO)
# ────────────────────────────────────────────────────────
def _get_last_ack(parent_id: int, student_id: int):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT signed_at
            FROM signatures          -- ← було parent_signatures
            WHERE parent_id = %s
              AND student_id = %s
            ORDER BY signed_at DESC
            LIMIT 1
            """,
            (parent_id, student_id),
        )
        row = cur.fetchone()
        return row[0] if row else None


def _record_ack(parent_id: int, student_id: int):
    conn = get_db()
    with conn.cursor() as cur:
        # запобігаємо дублю за сьогодні через WHERE NOT EXISTS
        cur.execute(
            """
            INSERT INTO signatures(parent_id, student_id)
            SELECT %s, %s
            WHERE NOT EXISTS (
              SELECT 1
              FROM signatures
              WHERE parent_id=%s
                AND student_id=%s
                AND signed_at::date = CURRENT_DATE
            )
            """,
            (parent_id, student_id, parent_id, student_id),
        )
        conn.commit()

# ────────────────────────────────────────────────────────
#  ПАНЕЛЬ
# ────────────────────────────────────────────────────────
@parent_bp.route("/parent")
def parent_dashboard():
    if session.get("role") != "parent":
        return redirect(url_for("auth.login"))
    return render_template("parent/parent_dashboard.html")

# ────────────────────────────────────────────────────────
#  CRUD API /api/parents
# ────────────────────────────────────────────────────────
@parent_bp.route("/api/parents", methods=["GET"])
def get_parents():
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT user_id, first_name, last_name, phone FROM parents")
        rows = cur.fetchall()
    return jsonify(
        [dict(zip(["user_id", "first_name", "last_name", "phone"], r)) for r in rows]
    )


@parent_bp.route("/api/parents", methods=["POST"])
def add_parent():
    data = request.get_json()
    first_name = data.get("first_name")
    last_name  = data.get("last_name")
    phone      = data.get("phone")
    if not all([first_name, last_name, phone]):
        return jsonify({"error": "Missing data"}), 400

    conn = get_db()
    with conn.cursor() as cur:
        # 🔍 Перевірка на унікальність номера
        cur.execute("SELECT 1 FROM parents WHERE phone = %s", (phone,))
        if cur.fetchone():
            return jsonify({"success": False, "error": "❗ Цей номер телефону вже зареєстрований"}), 400

        # ⏳ Створення з тимчасовим email
        cur.execute(
            """
            INSERT INTO users (email, password_hash, role)
            VALUES (%s, %s, %s)
            RETURNING user_id
            """,
            ("temp@school.com", "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f", "parent"),
        )
        user_id = cur.fetchone()[0]

        email = f"p{user_id}.{first_name.lower()}_{last_name.lower()}@school.com"
        cur.execute("UPDATE users SET email = %s WHERE user_id = %s", (email, user_id))

        cur.execute(
            """
            INSERT INTO parents (user_id, first_name, last_name, phone)
            VALUES (%s, %s, %s, %s)
            """,
            (user_id, first_name, last_name, phone),
        )
        conn.commit()

    return jsonify({"success": True})


@parent_bp.route("/api/parents/<int:user_id>", methods=["PUT"])
def update_parent(user_id):
    data = request.get_json()
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    phone = data.get("phone")

    conn = get_db()
    with conn.cursor() as cur:
        # 🔍 Перевірити, чи телефон уже є в когось іншого
        cur.execute("SELECT user_id FROM parents WHERE phone = %s", (phone,))
        row = cur.fetchone()
        if row and row[0] != user_id:
            return jsonify({"success": False, "error": "❗ Цей номер вже використовується іншим користувачем"}), 400

        email = f"p{user_id}.{first_name.lower()}_{last_name.lower()}@school.com"
        cur.execute("UPDATE users SET email=%s WHERE user_id=%s", (email, user_id))
        cur.execute("""
            UPDATE parents
            SET first_name=%s, last_name=%s, phone=%s
            WHERE user_id=%s
        """, (first_name, last_name, phone, user_id))

        conn.commit()

    return jsonify({"success": True})

@parent_bp.route("/api/parents/<int:user_id>", methods=["GET"])
def get_single_parent(user_id):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT p.user_id, p.first_name, p.last_name,
                   p.phone, u.email
            FROM parents p
            JOIN users u ON p.user_id = u.user_id
            WHERE p.user_id = %s
            """,
            (user_id,),
        )
        row = cur.fetchone()

    if not row:
        return jsonify({"error": "Parent not found"}), 404

    return jsonify(
        {
            "user_id":    row[0],
            "first_name": row[1],
            "last_name":  row[2],
            "phone":      row[3],
            "email":      row[4],
        }
    )


@parent_bp.route("/api/parents/<int:user_id>", methods=["DELETE"])
def delete_parent(user_id):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM parents WHERE user_id=%s", (user_id,))
        cur.execute("DELETE FROM users   WHERE user_id=%s", (user_id,))
        conn.commit()
    return jsonify({"success": True})

# ────────────────────────────────────────────────────────
#  ЩОДЕННИК
# ────────────────────────────────────────────────────────
@parent_bp.route("/parent/diary")
def parent_diary():
    if session.get("role") != "parent":
        return redirect(url_for("auth.login"))

    parent_id = session["user_id"]
    student   = get_student_by_parent(parent_id)
    if not student:
        return "Учень не знайдений", 404

    # Визначаємо початок тижня (понеділок)
    ws = request.args.get("week_start")
    try:
        week_start = (
            date.fromisoformat(ws)
            if ws
            else date.today() - timedelta(days=date.today().weekday())
        )
    except ValueError:
        week_start = date.today() - timedelta(days=date.today().weekday())
    week_end  = week_start + timedelta(days=6)
    prev_week = (week_start - timedelta(days=7)).isoformat()
    next_week = (week_start + timedelta(days=7)).isoformat()

    # Формуємо дані щоденника
    diary = []
    for offset in range(7):
        curr = week_start + timedelta(days=offset)
        dow  = curr.isoweekday()

        lessons = (
            Lesson.query
            .filter_by(class_id=student["class_id"], day=dow)
            .order_by(Lesson.start_time)
            .all()
        )

        lessons_data = []
        for ls in lessons:
            hw = (
                Homework.query
                .filter(
                    Homework.lesson_id == ls.lesson_id,
                    func.date(Homework.deadline) == curr,
                ).first()
            )
            grades = (
                Grade.query
                .filter(
                    and_(
                        Grade.student_id == student["user_id"],
                        Grade.lesson_id == ls.lesson_id,
                        func.date(Grade.grade_date) == curr  # ← дата уроку
                    )
                )
                .all()
            )
            att = Attendance.query.filter_by(
                student_id=student["user_id"], lesson_id=ls.lesson_id
            ).first()

            lessons_data.append(
                {"lesson": ls, "homework": hw,
                 "grades": grades, "attendance": att}
            )

        diary.append({"date": curr, "lessons": lessons_data})

    # Час останнього підпису
    acknowledged = _get_last_ack(parent_id, student["user_id"])

    return render_template(
        "parent/diary.html",
        student=student,
        diary=diary,
        week_start=week_start,
        week_end=week_end,
        prev_week=prev_week,
        next_week=next_week,
        acknowledged=acknowledged,
    )


@parent_bp.route("/parent/diary/ack", methods=["POST"])
def parent_diary_ack():
    if session.get("role") != "parent":
        return redirect(url_for("auth.login"))

    parent_id = session["user_id"]
    student   = get_student_by_parent(parent_id)
    _record_ack(parent_id, student["user_id"])

    # Залишаємо користувача на тій самій сторінці
    return redirect(request.referrer or url_for("parent.parent_diary"))
