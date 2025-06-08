from app.utils.db import get_db

def record_acknowledgement(parent_id: int, student_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO parent_acknowledgements (parent_id, student_id, acknowledged_at)
        VALUES (%s, %s, NOW())
        ON CONFLICT (parent_id, student_id)
        DO UPDATE SET acknowledged_at = NOW();
    """, (parent_id, student_id))
    conn.commit()
    cur.close()

def has_acknowledged(parent_id: int, student_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT acknowledged_at
          FROM parent_acknowledgements
         WHERE parent_id=%s AND student_id=%s
    """, (parent_id, student_id))
    row = cur.fetchone()
    cur.close()
    return row  # None або кортеж із datetime
