"""Flask application configuration settings.

Defines configuration classes (e.g., Config, DevelopmentConfig, ProductionConfig, TestConfig)
for different deployment environments. Loads sensitive values from environment
variables and provides default settings.
"""

import os

from dotenv import load_dotenv


# Constants
BASEDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Load environment variables
load_dotenv(os.path.join(BASEDIR, ".env"))


# Data Classes / Config Classes
class Config:
    """Base configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY") or "a-hard-to-guess-string"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///" + os.path.join(
        os.path.dirname(__file__), "database.db"
    )


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SECRET_KEY = os.environ.get("SECRET_KEY")


class TestConfig(Config):
    """Test configuration."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    SERVER_NAME = "localhost.localdomain"


# Factory Functions
def get_config():
    """Get the correct config class based on FLASK_ENV environment variable."""
    env = os.environ.get("FLASK_ENV", "development")
    if env == "production":
        return ProductionConfig
    elif env == "testing":
        return TestConfig
    else:
        return DevelopmentConfig
