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
from calendar import monthrange
from app.utils.db import get_db
from app.dao.students_dao import get_student_by_parent
from app.models import Lesson, Homework, Grade, Attendance
from app.dao.students_dao import get_student_by_id
parent_bp = Blueprint("parent", __name__)




# ── Допоміжна функція для вибору поточної дитини ──
def get_current_student():
    sid = session.get('student_id')
    if not sid:
        return None
    # Витягуємо студента по id
    return get_student_by_id(sid)
# ---- Функції підпису ----
# --- Функції підпису ---
def _get_last_ack(parent_id: int, student_id: int):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT signed_at FROM signatures "
            "WHERE parent_id=%s AND student_id=%s "
            "ORDER BY signed_at DESC LIMIT 1",
            (parent_id, student_id),
        )
        r = cur.fetchone()
    return r[0] if r else None

def _record_ack(parent_id: int, student_id: int):
    conn = get_db()
    with conn.cursor() as cur:
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

# --- Головна сторінка батьків ---
@parent_bp.route("/parent")
def parent_dashboard():
    if session.get("role") != "parent":
        return redirect(url_for("auth.login"))

    parent_id = session["user_id"]
    conn = get_db()


    # Дані батька
    with conn.cursor() as cur:
        cur.execute("SELECT first_name, last_name FROM parents WHERE user_id = %s", (parent_id,))
        row = cur.fetchone()
        parent = {"first_name": row[0], "last_name": row[1]}

    # Знайти учня
    student = get_current_student()
    if not student:
        return "Учень не знайдений", 404

    # Дати тижня
    today = date.today()
    from calendar import monthrange

    month_start = today.replace(day=1)
    days_in_month = monthrange(today.year, today.month)[1]
    month_dates = [month_start + timedelta(days=i) for i in range(days_in_month)]
    month_name = today.strftime('%B %Y')  # наприклад, 'Липень 2025'
    week_start = today - timedelta(days=today.weekday())
    week_dates = [week_start + timedelta(days=i) for i in range(7)]
    week_end = week_start + timedelta(days=6)

    # Останній підпис
    with conn.cursor() as cur:
        cur.execute("""
            SELECT signed_at FROM signatures
            WHERE parent_id=%s AND student_id=%s
            ORDER BY signed_at DESC LIMIT 1
        """, (parent_id, student["user_id"]))
        row = cur.fetchone()
        last_ack = row[0] if row else None

    # Календар підпису (дні, коли підписано)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT signed_at::date
            FROM signatures
            WHERE parent_id=%s AND student_id=%s
              AND signed_at::date BETWEEN %s AND %s
        """, (parent_id, student["user_id"], week_start, week_end))
        signature_dates = {r[0] for r in cur.fetchall()}

    with conn.cursor() as cur:
        cur.execute("""
            SELECT signed_at::date
            FROM signatures
            WHERE parent_id=%s AND student_id=%s
              AND signed_at::date BETWEEN %s AND %s
        """, (parent_id, student["user_id"], month_start, month_start + timedelta(days=days_in_month - 1)))
        signature_dates_month = {r[0] for r in cur.fetchall()}

    # Середній бал за тиждень
    with conn.cursor() as cur:
        cur.execute("""
            SELECT AVG(grade_value)
            FROM grades g
            JOIN lesson_sessions s ON g.session_id = s.session_id
            WHERE g.student_id=%s AND s.session_date BETWEEN %s AND %s
        """, (student["user_id"], week_start, week_end))
        avg_grade = cur.fetchone()[0]
        avg_grade = round(avg_grade, 2) if avg_grade else None

    # Відвідуваність (%)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*),
                   SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END)
            FROM attendance a
            JOIN lesson_sessions s ON a.session_id = s.session_id
            WHERE a.student_id=%s
              AND s.session_date BETWEEN %s AND %s
        """, (student["user_id"], week_start, week_end))
        total, present = cur.fetchone()
        attendance_percent = round((present / total) * 100, 1) if total and present is not None else None

    # Новини (захардкожено)
    news_list = [
        "Додано нову функцію підпису щоденника.",
        "Вітаємо з новим навчальним тижнем!",
    ]

    return render_template(
        "parent/parent_dashboard.html",
        parent=parent,
        last_ack=last_ack,
        avg_grade=avg_grade,
        attendance_percent=attendance_percent,
        week_dates=week_dates,
        signature_dates=signature_dates,
        news_list=news_list,
        month_dates=month_dates,
        month_name=month_name,
        signature_dates_month=signature_dates_month,
        today=today,
    )


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
        # Створюємо користувача
        cur.execute(
            """
            INSERT INTO users (email, password_hash, role)
            VALUES (%s, %s, %s)
            RETURNING user_id
            """,
            (
                f"parent.{first_name.lower()}_{last_name.lower()}@school.com",
                # sha-256 від "password"
                "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f",
                "parent",
            ),
        )
        user_id = cur.fetchone()[0]

        # Додаємо в таблицю parents
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
    email = f"parent.{first_name.lower()}_{last_name.lower()}@school.com"

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("UPDATE users SET email=%s WHERE user_id=%s", (email, user_id))
        cur.execute(
            """
            UPDATE parents
            SET first_name=%s, last_name=%s, phone=%s
            WHERE user_id=%s
            """,
            (first_name, last_name, phone, user_id),
        )
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

@parent_bp.route("/parent/diary")
def parent_diary():
    if session.get("role") != "parent":
        return redirect(url_for("auth.login"))

    parent_id = session["user_id"]
    student = get_current_student()
    if not student:
        return "Учень не знайдений", 404

    conn = get_db()

    # ── 1. Межі тижня ─────────────────────────────────────
    ws = request.args.get("week_start")
    try:
        week_start = date.fromisoformat(ws) if ws else date.today() - timedelta(days=date.today().weekday())
    except ValueError:
        week_start = date.today() - timedelta(days=date.today().weekday())
    week_dates = [week_start + timedelta(days=i) for i in range(7)]
    week_end = week_start + timedelta(days=6)
    prev_week = (week_start - timedelta(days=7)).isoformat()
    next_week = (week_start + timedelta(days=7)).isoformat()

    # ── 2. Розклад: lessons ──────────────────────────────
    with conn.cursor() as cur:
        cur.execute("""
            SELECT lesson_id, day, start_time, end_time, subject_id
            FROM lessons
            WHERE class_id = %s
            ORDER BY day, start_time
        """, (student["class_id"],))
        lessons = cur.fetchall()

    # ── 3. Предмети ──────────────────────────────────────
    subject_ids = tuple({l[4] for l in lessons}) or (0,)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT subject_id, title
            FROM subjects
            WHERE subject_id IN %s
        """, (subject_ids,))
        subj_map = {sid: title for sid, title in cur.fetchall()}

    # ── 4. Сесії ──────────────────────────────────────────
    with conn.cursor() as cur:
        cur.execute("""
            SELECT session_id, lesson_id, session_date
            FROM lesson_sessions
            WHERE session_date BETWEEN %s AND %s
        """, (week_start, week_end))
        sess = cur.fetchall()
    session_map = {(lesson_id, session_date): session_id for session_id, lesson_id, session_date in sess}

    # ── 5. Домашки ───────────────────────────────────────
    session_ids = tuple(session_map.values()) or (0,)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT session_id, description
            FROM homework
            WHERE session_id IN %s
        """, (session_ids,))
        hw_map = {sid: desc for sid, desc in cur.fetchall()}

    # ── 6. Оцінки ─────────────────────────────────────────
    with conn.cursor() as cur:
        cur.execute("""
            SELECT session_id, grade_value
            FROM grades
            WHERE session_id IN %s AND student_id = %s
        """, (session_ids, student["user_id"]))
        grades_map = {sid: gv for sid, gv in cur.fetchall()}

    # ── 7. Відвідуваність ─────────────────────────────────
    with conn.cursor() as cur:
        cur.execute("""
            SELECT session_id, status
            FROM attendance
            WHERE session_id IN %s AND student_id = %s
        """, (session_ids, student["user_id"]))
        att_map = {sid: st for sid, st in cur.fetchall()}

    # ── 8. Формуємо diary ─────────────────────────────────
    diary = {}
    for lesson_id, day_of_week, start, end, subject_id in lessons:
        for curr_date in week_dates:
            if curr_date.isoweekday() == day_of_week:
                sid = session_map.get((lesson_id, curr_date))
                diary.setdefault(curr_date, []).append({
                    "time": f"{start:%H:%M}–{end:%H:%M}",
                    "subject": subj_map.get(subject_id, "—"),
                    "homework": hw_map.get(sid, "—"),
                    "grade": grades_map.get(sid, "—"),
                    "attendance": att_map.get(sid, "—"),
                })

    # ── 9. Підпис за сьогодні ────────────────────────────
    with conn.cursor() as cur:
        cur.execute(
            "SELECT 1 FROM signatures WHERE parent_id=%s AND student_id=%s AND signed_at::date = %s",
            (parent_id, student["user_id"], date.today())
        )
        ack_today = bool(cur.fetchone())

    # ── 10. Останній підпис ───────────────────────────────
    with conn.cursor() as cur:
        cur.execute(
            "SELECT signed_at FROM signatures WHERE parent_id=%s AND student_id=%s ORDER BY signed_at DESC LIMIT 1",
            (parent_id, student["user_id"])
        )
        r = cur.fetchone()
        last_ack = r[0] if r else None

    # ── 11. Місячний календар ─────────────────────────────
    today = date.today()
    month_start = today.replace(day=1)
    days_in_month = monthrange(today.year, today.month)[1]
    month_dates = [month_start + timedelta(days=i) for i in range(days_in_month)]
    month_name = today.strftime('%B %Y')

    with conn.cursor() as cur:
        cur.execute(
            "SELECT DISTINCT signed_at::date FROM signatures "
            "WHERE parent_id=%s AND student_id=%s AND signed_at::date BETWEEN %s AND %s",
            (parent_id, student["user_id"], month_start, month_start + timedelta(days=days_in_month-1))
        )
        signature_dates_month = {row[0] for row in cur.fetchall()}

    return render_template(
        "parent/diary.html",
        student=student,
        diary=diary,
        week_dates=week_dates,
        week_start=week_start,
        week_end=week_end,
        prev_week=prev_week,
        next_week=next_week,
        ack_today=ack_today,
        last_ack=last_ack,
        today=today,
        month_dates=month_dates,
        month_name=month_name,
        signature_dates_month=signature_dates_month,
    )


@parent_bp.route("/parent/diary/ack", methods=["POST"])
def parent_diary_ack():
    if session.get("role") != "parent":
        return redirect(url_for("auth.login"))

    parent_id = session["user_id"]
    student   = get_student_by_parent(parent_id)
    _record_ack(parent_id, student["user_id"])
    return redirect(request.referrer or url_for("parent.parent_diary"))

@parent_bp.route("/parent/attendance")
def parent_attendance():
    if session.get("role") != "parent":
        return redirect(url_for("auth.login"))

    parent_id = session["user_id"]
    student = get_current_student()
    if not student:
        return "Учень не знайдений", 404

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT s.session_date, sub.title, a.status, a.comment
            FROM attendance a
            JOIN lesson_sessions s ON a.session_id = s.session_id
            JOIN lessons l ON s.lesson_id = l.lesson_id
            JOIN subjects sub ON l.subject_id = sub.subject_id
            WHERE a.student_id = %s
            ORDER BY s.session_date DESC
        """, (student["user_id"],))
        attendance_list = cur.fetchall()

    # Порахувати % відвідуваності (за весь час або за останній тиждень)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*), SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END)
            FROM attendance
            WHERE student_id=%s
        """, (student["user_id"],))
        total, present = cur.fetchone()
        attendance_percent = round((present / total) * 100, 1) if total else None

    return render_template(
        "parent/attendance.html",
        student=student,
        attendance_list=attendance_list,
        attendance_percent=attendance_percent
    )
@parent_bp.route("/parent/announcements")
def parent_announcements():
    if session.get("role") != "parent":
        return redirect(url_for("auth.login"))

    parent_id = session["user_id"]
    student   = get_student_by_parent(parent_id)
    if not student:
        return "Учень не знайдений", 404

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT created_at, title, text
            FROM announcements
            ORDER BY created_at DESC
        """)
        rows = cur.fetchall()

    announcements = [
        {"date": r[0], "title": r[1], "text": r[2]}
        for r in rows
    ]

    return render_template(
        "parent/announcements.html",
        student=student,
        announcements=announcements,
    )

@parent_bp.route('/parent/choose-child')
def choose_child():
    if session.get('role') != 'parent' or 'children' not in session:
        return redirect(url_for('auth.login'))
    children = session['children']
    return render_template('parent/choose_child.html', children=children)

@parent_bp.route('/parent/select-child/<int:student_id>')
def select_child(student_id):
    # Перевір, що цей student_id належить до session['children']
    allowed = [c["user_id"] for c in session.get("children", [])]
    if student_id not in allowed:
        flash("Ви не маєте доступу до цього профілю", "danger")
        return redirect(url_for('parent.choose_child'))
    session['student_id'] = student_id
    return redirect(url_for('parent.parent_dashboard'))
