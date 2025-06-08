from datetime import datetime, timezone
from app.utils.db import get_db


class StudentPortalDAO:
    # ---------- HOMEWORK ----------
    @staticmethod
    def homework_list(student_id: int):
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT h.homework_id,
                   s.title,
                   h.description,
                   h.deadline,
                   g.grade_value,
                   g.comment,
                   (hs.homework_id IS NOT NULL) AS done
            FROM homework h
            JOIN lessons  l  ON l.lesson_id  = h.lesson_id
            JOIN subjects s  ON s.subject_id = l.subject_id
            LEFT JOIN grades g
                   ON g.lesson_id  = h.lesson_id
                  AND g.student_id = %s
            LEFT JOIN homework_submissions hs
                   ON hs.homework_id = h.homework_id
                  AND hs.student_id  = %s
            WHERE l.class_id = (SELECT class_id FROM students WHERE user_id = %s)
            ORDER BY h.deadline DESC
            """,
            (student_id, student_id, student_id),
        )
        rows = cur.fetchall()
        cur.close()
        return [
            {
                "homework_id": r[0],
                "subject":     r[1],
                "description": r[2],
                "deadline":    r[3].isoformat(),
                "grade":       r[4],
                "comment":     r[5],
                "done":        bool(r[6]),
            }
            for r in rows
        ]

    @staticmethod
    def toggle_done(student_id: int, homework_id: int):
        conn = get_db()
        cur = conn.cursor()

        # дедлайн
        cur.execute(
            "SELECT deadline FROM homework WHERE homework_id = %s",
            (homework_id,),
        )
        row = cur.fetchone()
        if not row:
            raise ValueError("homework not found")

        deadline = row[0].replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > deadline:
            return False  # після дедлайну міняти не можна

        # чи вже позначено?
        cur.execute(
            """
            SELECT 1 FROM homework_submissions
            WHERE homework_id = %s AND student_id = %s
            """,
            (homework_id, student_id),
        )
        exists = cur.fetchone() is not None

        if exists:
            # скасовуємо
            cur.execute(
                """
                DELETE FROM homework_submissions
                WHERE homework_id = %s AND student_id = %s
                """,
                (homework_id, student_id),
            )
            new_state = False
        else:
            # відмічаємо
            cur.execute(
                """
                INSERT INTO homework_submissions (homework_id, student_id)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
                """,
                (homework_id, student_id),
            )
            new_state = True

        conn.commit()
        cur.close()
        return new_state

    # ---------- інші DAO-методи (без змін) ----------
    @staticmethod
    def schedule(student_id: int):
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT l.lesson_id, l.day, l.start_time, l.end_time,
                   s.title, r.room_number,
                   t.last_name || ' ' || t.first_name
            FROM lessons l
            JOIN students  st ON st.class_id  = l.class_id
            JOIN subjects  s  ON s.subject_id = l.subject_id
            JOIN teachers  t  ON t.user_id    = l.teacher_id
            JOIN rooms     r  ON r.room_id    = l.room_id
            WHERE st.user_id = %s
            ORDER BY l.day, l.start_time
            """,
            (student_id,),
        )
        rows = cur.fetchall()
        cur.close()
        return [
            {
                "lesson_id": r[0],
                "day":       r[1],
                "start":     str(r[2]),
                "end":       str(r[3]),
                "subject":   r[4],
                "room":      r[5],
                "teacher":   r[6],
            }
            for r in rows
        ]

    @staticmethod
    def attendance(student_id: int):
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT a.attendance_id,
                   s.title,
                   a.status,
                   a.comment,
                   l.day,
                   l.start_time
            FROM attendance a
            JOIN lessons  l ON l.lesson_id  = a.lesson_id
            JOIN subjects s ON s.subject_id = l.subject_id
            WHERE a.student_id = %s
            ORDER BY l.day DESC, l.start_time DESC
            """,
            (student_id,),
        )
        rows = cur.fetchall()
        cur.close()
        return [
            {
                "attendance_id": r[0],
                "subject":       r[1],
                "status":        r[2],
                "comment":       r[3],
                "day":           r[4],
                "start":         str(r[5]),
            }
            for r in rows
        ]

    @staticmethod
    def teachers(student_id: int):
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT DISTINCT t.user_id, t.first_name, t.last_name, r.room_number
            FROM lessons l
            JOIN students s ON s.class_id = l.class_id
            JOIN teachers t ON t.user_id  = l.teacher_id
            JOIN rooms    r ON r.room_id  = l.room_id
            WHERE s.user_id = %s
            ORDER BY t.last_name
            """,
            (student_id,),
        )
        rows = cur.fetchall()
        cur.close()
        return [
            {
                "teacher_id": r[0],
                "first_name": r[1],
                "last_name":  r[2],
                "room":       r[3],
            }
            for r in rows
        ]

    @staticmethod
    def announcements():
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT announcement_id,title,text,created_at "
            "FROM announcements ORDER BY created_at DESC LIMIT 20"
        )
        rows = cur.fetchall()
        cur.close()
        return [
            {
                "announcement_id": r[0],
                "title":  r[1],
                "text":   r[2],
                "created_at": r[3].isoformat(),
            }
            for r in rows
        ]

    # ---------- TEACHERS + ROOMS (одна таблиця) ----------
    @staticmethod
    def teachers_and_rooms(student_id: int):
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT t.user_id,
                   t.first_name,
                   t.last_name,
                   ARRAY_AGG(DISTINCT s.title)      AS subjects,
                   ARRAY_AGG(DISTINCT r.room_number) AS rooms
            FROM lessons l
            JOIN students  st ON st.class_id = l.class_id
            JOIN teachers  t  ON t.user_id   = l.teacher_id
            JOIN subjects  s  ON s.subject_id = l.subject_id
            JOIN rooms     r  ON r.room_id   = l.room_id
            WHERE st.user_id = %s
            GROUP BY t.user_id, t.first_name, t.last_name
            ORDER BY t.last_name
            """,
            (student_id,),
        )
        data = [
            {
                "teacher_id": r[0],
                "first_name": r[1],
                "last_name": r[2],
                "subjects": r[3],  # список предметів
                "rooms": r[4],  # список номерів кабінетів
            }
            for r in cur.fetchall()
        ]
        cur.close()
        return data
