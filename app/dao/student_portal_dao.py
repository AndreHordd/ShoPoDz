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
            -- спочатку приєднуємо сесію уроку
            JOIN lesson_sessions ls ON ls.session_id = h.session_id
            JOIN lessons        l  ON l.lesson_id   = ls.lesson_id
            JOIN subjects       s  ON s.subject_id  = l.subject_id
            LEFT JOIN grades g
                   ON g.session_id = ls.session_id
                  AND g.student_id = %s
            LEFT JOIN homework_submissions hs
                   ON hs.homework_id = h.homework_id
                  AND hs.student_id  = %s
            WHERE l.class_id = (
                SELECT class_id FROM students WHERE user_id = %s
            )
            ORDER BY h.deadline DESC
            """,
            (student_id, student_id, student_id),
        )
        rows = cur.fetchall()
        cur.close()
        return [
            {
                "homework_id": r[0],
                "subject": r[1],
                "description": r[2],
                "deadline": r[3].isoformat(),
                "grade": r[4],
                "comment": r[5],
                "done": bool(r[6]),
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
            SELECT l.lesson_id, l.day, 
                   TO_CHAR(l.start_time, 'HH24:MI') as start_time, 
                   TO_CHAR(l.end_time, 'HH24:MI') as end_time,
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
                "start_time": r[2],
                "end_time":   r[3],
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
                   ls.session_date,
                   l.start_time
            FROM attendance a
            -- приєднуємо спочатку сесію уроку
            JOIN lesson_sessions ls ON ls.session_id = a.session_id
            JOIN lessons        l  ON l.lesson_id   = ls.lesson_id
            JOIN subjects       s  ON s.subject_id  = l.subject_id
            WHERE a.student_id = %s
            ORDER BY ls.session_date DESC, l.start_time DESC
            """,
            (student_id,),
        )
        rows = cur.fetchall()
        cur.close()
        return [
            {
                "attendance_id": r[0],
                "subject": r[1],
                "status": r[2],
                "comment": r[3],
                "day": r[4].isoformat(),
                "start": str(r[5]),
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

    @staticmethod
    def profile(student_id: int):
        conn = get_db()
        cur = conn.cursor()
        
        # Основная информация о студенте
        cur.execute(
            """
            SELECT s.user_id, s.first_name, s.last_name, s.email,
                   c.class_number, c.subclass,
                   c.class_number || c.subclass AS class_name
            FROM students s
            JOIN classes c ON c.class_id = s.class_id
            WHERE s.user_id = %s
            """,
            (student_id,),
        )
        student_row = cur.fetchone()
        
        if not student_row:
            cur.close()
            return None
            
        # Статистика по домашним заданиям
        cur.execute(
            """
            SELECT 
                COUNT(*) AS total_homework,
                COUNT(hs.homework_id) AS completed_homework
            FROM homework h
            JOIN lesson_sessions ls ON ls.session_id = h.session_id
            JOIN lessons l ON l.lesson_id = ls.lesson_id
            LEFT JOIN homework_submissions hs ON hs.homework_id = h.homework_id AND hs.student_id = %s
            WHERE l.class_id = (SELECT class_id FROM students WHERE user_id = %s)
            """,
            (student_id, student_id),
        )
        homework_stats = cur.fetchone()
        
        # Статистика по посещаемости
        cur.execute(
            """
            SELECT 
                COUNT(*) AS total_lessons,
                COUNT(CASE WHEN a.status = 'present' THEN 1 END) AS present_count,
                COUNT(CASE WHEN a.status = 'absent' THEN 1 END) AS absent_count,
                COUNT(CASE WHEN a.status = 'late' THEN 1 END) AS late_count,
                COUNT(CASE WHEN a.status = 'excused' THEN 1 END) AS excused_count
            FROM attendance a
            JOIN lesson_sessions ls ON ls.session_id = a.session_id
            WHERE a.student_id = %s
            """,
            (student_id,),
        )
        attendance_stats = cur.fetchone()
        
        # Средний балл
        cur.execute(
            """
            SELECT AVG(CAST(g.grade_value AS DECIMAL)) AS avg_grade
            FROM grades g
            JOIN lesson_sessions ls ON ls.session_id = g.session_id
            JOIN lessons l ON l.lesson_id = ls.lesson_id
            WHERE g.student_id = %s AND g.grade_value IS NOT NULL
            """,
            (student_id,),
        )
        grade_stats = cur.fetchone()
        
        # Количество одноклассников
        cur.execute(
            """
            SELECT COUNT(*) - 1 AS classmates_count
            FROM students
            WHERE class_id = (SELECT class_id FROM students WHERE user_id = %s)
            """,
            (student_id,),
        )
        classmates_count = cur.fetchone()
        
        cur.close()
        
        # Формируем результат с безопасной обработкой None значений
        homework_total = homework_stats[0] if homework_stats else 0
        homework_completed = homework_stats[1] if homework_stats else 0
        homework_rate = round((homework_completed / homework_total * 100) if homework_total > 0 else 0, 1)
        
        attendance_total = attendance_stats[0] if attendance_stats else 0
        attendance_present = attendance_stats[1] if attendance_stats else 0
        attendance_absent = attendance_stats[2] if attendance_stats else 0
        attendance_late = attendance_stats[3] if attendance_stats else 0
        attendance_excused = attendance_stats[4] if attendance_stats else 0
        attendance_rate = round((attendance_present / attendance_total * 100) if attendance_total > 0 else 0, 1)
        
        avg_grade = None
        if grade_stats and grade_stats[0] is not None:
            avg_grade = round(float(grade_stats[0]), 2)
        
        profile_data = {
            "student_id": student_row[0],
            "first_name": student_row[1],
            "last_name": student_row[2],
            "email": student_row[3] or "Не вказано",
            "class_number": student_row[4],
            "subclass": student_row[5] or "",
            "class_name": student_row[6],
            "classmates_count": classmates_count[0] if classmates_count else 0,
            "homework_stats": {
                "total": homework_total,
                "completed": homework_completed,
                "completion_rate": homework_rate
            },
            "attendance_stats": {
                "total": attendance_total,
                "present": attendance_present,
                "absent": attendance_absent,
                "late": attendance_late,
                "excused": attendance_excused,
                "attendance_rate": attendance_rate
            },
            "average_grade": avg_grade
        }
        
        return profile_data
