from app.models import db, User

def get_user_by_email_from_db(email):
    return db.session.query(User).filter_by(email=email).first()
