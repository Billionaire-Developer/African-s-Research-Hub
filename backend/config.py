import os
from datetime import timedelta

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


def normalize_postgres_url(url: str) -> str:
    """
    Normalize PostgreSQL database URLs for SQLAlchemy:
    - Convert postgres:// → postgresql://
    - Convert postgresql:// → postgresql+psycopg2:// if psycopg2 is not added
    """

    if url.startswith("postgres://"):
        # Heroku-style fix
        url = "postgresql://" + url[len("postgres://") :]

    if url.startswith("postgresql://"):
        if not url.startswith("postgresql+psycopg2://"):
            url = "postgresql+psycopg2://" + url[len("postgresql://") :]

    return url


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY")
    DATABASE_URL = os.environ.get("DATABASE_URL") or "sqlite:///" + os.path.join(
        basedir, "app.db"
    )
    SQLALCHEMY_DATABASE_URI = normalize_postgres_url(DATABASE_URL)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Abstract Publication Fee
    ABSTRACT_PUBLICATION_FEE = os.environ.get("ABSTRACT_PUBLICATION_FEE") or 1.99

    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or SECRET_KEY
    JWT_ALGORITHM = "HS256"
    PASSWORD_RESET_TOKEN_EXPIRY = timedelta(minutes=5)

    # Session Configuration
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("FLASK_ENV") == "production"
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # File Upload Configuration
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max file size
    UPLOAD_FOLDER = os.path.join(basedir, "uploads", "abstracts")
    ALLOWED_EXTENSIONS = {"pdf"}

    # PayChangu Configurations
    PAYCHANGU_SECRET = os.getenv("PAYCHANGU_SECRET")

    # Email Configuration for cPanel
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 587)
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() in ["true", "on", "1"]
    MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL", "false").lower() in ["true", "on", "1",]
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER") or os.environ.get("MAIL_USERNAME")

    # Admin email for notifications
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")

    # Website URL for email links
    WEBSITE_URL = os.environ.get("WEBSITE_URL", "http://localhost:5000")
    FRONTEND_URL = os.getenv('FRONTEND_URL')

    # Additional cPanel-specific settings
    MAIL_DEBUG = os.environ.get("MAIL_DEBUG", "false").lower() in ["true", "on", "1"]
    MAIL_SUPPRESS_SEND = os.environ.get("MAIL_SUPPRESS_SEND", "false").lower() in ["true", "on", "1",]
