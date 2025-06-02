from app.dao.users_dao import get_user_by_email_from_db

def get_user_by_email(email):
    return get_user_by_email_from_db(email)
