import os
from dotenv import import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "secret123")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-key")
    db_url = os.getenv("DATABASE_URL", "sqlite:///local.db")
    db_url = db_url.replace("postgresql://", "postgresql+psycopg://")
    db_url = db_url.replace("postgresql+psycopg2://", "postgresql+psycopg://")
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.getenv("FLASK_DEBUG", "True") == "True"