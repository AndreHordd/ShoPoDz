from app.utils.db import get_db   # бере connection з psycopg2 / SQLAlchemy Engine

def get_teacher_schedule(teacher_id: int):
    """
    Повертає список уроків указаного вчителя у форматі list[dict].
    """
    sql = """
        SELECT  l.day,
                TO_CHAR(l.start_time,'HH24:MI') AS start_time,
                TO_CHAR(l.end_time,  'HH24:MI') AS end_time,
                CONCAT(c.class_number, c.subclass) AS class,
                s.title  AS subject,
                r.room_number
        FROM    lessons l
        JOIN    classes  c ON c.class_id   = l.class_id
        JOIN    subjects s ON s.subject_id = l.subject_id
        JOIN    rooms    r ON r.room_id    = l.room_id
        WHERE   l.teacher_id = %s
        ORDER BY l.day, l.start_time;
    """
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(sql, (teacher_id,))
        cols = ["day","start_time","end_time","class","subject","room_number"]
        return [dict(zip(cols, row)) for row in cur.fetchall()]
