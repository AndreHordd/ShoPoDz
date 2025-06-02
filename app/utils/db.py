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
