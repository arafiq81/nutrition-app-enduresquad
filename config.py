import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get absolute path to project directory
BASE_DIR = Path(__file__).resolve().parent

def _default_db_uri(filename: str = "nutrition.db") -> str:
    """Build the default SQLite URI using an absolute path."""
    return f"sqlite:///{BASE_DIR / 'data' / filename}"


def _resolve_db_uri() -> str:
    """
    Resolve the database URI.

    Render (and Heroku) set DATABASE_URL with the legacy 'postgres://' scheme.
    SQLAlchemy 1.4+ requires 'postgresql://'.  Fix it transparently here so
    the rest of the app never has to think about it.
    """
    url = os.getenv('DATABASE_URL', _default_db_uri())
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)
    return url


class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # DATABASE_URL env var allows swapping to PostgreSQL for cloud deployments.
    # Falls back to local SQLite when not set.
    SQLALCHEMY_DATABASE_URI = _resolve_db_uri()

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Anthropic API
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

    # App settings
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration — uses an isolated in-memory database."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
