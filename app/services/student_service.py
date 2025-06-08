from datetime import datetime
from psycopg2.extras import RealDictCursor
from app.utils.db import get_db


class StudentService:
    """
    Агрегує всі запити, потрібні на учнівських сторінках.
    Працює без ORM, напряму через psycopg2 та RealDictCursor.
    """

    @staticmethod
    def _fetch_all(query: str, params: tuple) -> list[dict]:
        conn = get_db()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            return cur.fetchall()

    # ---------- РОЗКЛАД ----------
    @classmethod
    def get_weekly_schedule(cls, student_id: int) -> list[dict]:
        sql = """
        SELECT l.lesson_id,
               l.day,
               to_char(l.start_time, 'HH24:MI')  AS start_time,
               to_char(l.end_time,   'HH24:MI')  AS end_time,
               s.title                           AS subject,
               CONCAT(t.last_name, ' ', t.first_name) AS teacher,
               r.room_number                     AS room
          FROM students        st
          JOIN lessons         l  ON l.class_id   = st.class_id
          JOIN subjects        s  ON s.subject_id = l.subject_id
          JOIN teachers        t  ON t.user_id    = l.teacher_id
          JOIN rooms           r  ON r.room_id    = l.room_id
         WHERE st.user_id = %s
         ORDER BY l.day, l.start_time;
        """
        return cls._fetch_all(sql, (student_id,))

    # ---------- ДОМАШНЄ ЗАВДАННЯ ----------
    @classmethod
    def get_homework(cls, student_id: int) -> list[dict]:
        sql = """
        SELECT h.homework_id,
               h.description,
               to_char(h.deadline, 'YYYY-MM-DD HH24:MI') AS deadline,
               COALESCE(shs.completed, FALSE)           AS completed,
               COALESCE(to_char(shs.completed_at, 'YYYY-MM-DD HH24:MI'), '') AS completed_at
          FROM students                    st
          JOIN lessons                     l   ON l.class_id   = st.class_id
          JOIN homework                    h   ON h.lesson_id  = l.lesson_id
     LEFT JOIN student_homework_status    shs ON shs.homework_id = h.homework_id
                                              AND shs.student_id  = st.user_id
         WHERE st.user_id = %s
         ORDER BY h.deadline;
        """
        return cls._fetch_all(sql, (student_id,))

    @staticmethod
    def toggle_homework_completion(student_id: int, homework_id: int) -> bool:
        """
        Інвертує статус виконання. Повертає новий completed (True/False).
        """
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO student_homework_status (student_id, homework_id, completed,
                                                     completed_at)
                VALUES (%s, %s, TRUE, %s)
                ON CONFLICT (student_id, homework_id)
                DO UPDATE SET completed    = NOT student_homework_status.completed,
                              completed_at = CASE
                                  WHEN NOT student_homework_status.completed
                                        THEN NOW()
                                  ELSE NULL END
                RETURNING completed;
            """, (student_id, homework_id, datetime.utcnow()))
            completed, = cur.fetchone()
        conn.commit()
        return completed

    # ---------- ОЦІНКИ ----------
    @classmethod
    def get_grades(cls, student_id: int) -> list[dict]:
        sql = """
        SELECT g.grade_id,
               s.title                AS subject,
               g.grade_value          AS grade,
               to_char(l.start_time, 'YYYY-MM-DD') AS lesson_date,
               CONCAT(t.last_name, ' ', t.first_name) AS teacher,
               COALESCE(g.comment, '') AS comment
          FROM grades   g
          JOIN lessons  l ON l.lesson_id = g.lesson_id
          JOIN subjects s ON s.subject_id = l.subject_id
          JOIN teachers t ON t.user_id    = g.teacher_id
         WHERE g.student_id = %s
         ORDER BY lesson_date DESC;
        """
        return cls._fetch_all(sql, (student_id,))

    # ---------- ВІДВІДУВАНІСТЬ ----------
    @classmethod
    def get_attendance(cls, student_id: int) -> list[dict]:
        sql = """
        SELECT a.attendance_id,
               s.title                AS subject,
               a.status,
               to_char(l.start_time, 'YYYY-MM-DD') AS lesson_date,
               COALESCE(a.comment, '') AS comment
          FROM attendance a
          JOIN lessons    l ON l.lesson_id = a.lesson_id
          JOIN subjects   s ON s.subject_id = l.subject_id
         WHERE a.student_id = %s
         ORDER BY lesson_date DESC;
        """
        return cls._fetch_all(sql, (student_id,))

    # ---------- ОГОЛОШЕННЯ ----------
    @classmethod
    def get_announcements(cls) -> list[dict]:
        sql = """
        SELECT announcement_id,
               title,
               text,
               to_char(created_at, 'YYYY-MM-DD HH24:MI') AS created_at
          FROM announcements
         ORDER BY created_at DESC
         LIMIT 30;
        """
        return cls._fetch_all(sql, tuple())
