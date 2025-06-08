import psycopg2
from flask import current_app, g

def get_db():
    """Створює та кешує під’єднання в flask.g."""
    if "db" not in g:
        g.db = psycopg2.connect(current_app.config["DB_URL"])
    return g.db

def close_db(error=None):
    """Закриває під’єднання після завершення запиту."""
    db = g.pop("db", None)
    if db:
        db.close()

def init_db():
    """Створює необхідні таблиці, якщо їх ще нема."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS parent_acknowledgements (
      parent_id       INTEGER NOT NULL
                        REFERENCES parents(user_id)
                        ON DELETE CASCADE,
      student_id      INTEGER NOT NULL
                        REFERENCES students(user_id)
                        ON DELETE CASCADE,
      acknowledged_at TIMESTAMP NOT NULL DEFAULT NOW(),
      PRIMARY KEY (parent_id, student_id)
    );
    """)
    conn.commit()
    cur.close()
