import os


class Config:
    # Используем SQLite по умолчанию, как в задании
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///parking.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
