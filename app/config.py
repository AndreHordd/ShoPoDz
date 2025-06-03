import os

class Config:
    # Секретний ключ Flask для сесій (можна згенерувати або захардкодити)
    SECRET_KEY = os.environ.get('SECRET_KEY', 'very-secret-key')

    # Підключення до PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://postgres:vladhulko2006@localhost/shopodz'
    )

    DB_URL = SQLALCHEMY_DATABASE_URI  # 🔥 Додаємо сюди!

    # Вимикає попередження SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Часовий пояс для застосунку (якщо використовуєш час)
    TIMEZONE = 'Europe/Kyiv'

    # Додатково (якщо потрібно)
    DEBUG = True
