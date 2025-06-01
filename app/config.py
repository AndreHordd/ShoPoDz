import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key")
    DB_URL = os.environ.get(
        "DATABASE_URL",
        "dbname=shopodz user=postgres password=vladhulko2006"
    )
