"""Initializes and configures Flask extensions.

Instantiates common Flask extensions (SQLAlchemy, Migrate, LoginManager, Bcrypt)
to avoid circular dependencies within the application factory pattern.
Includes configuration specific to these extensions.
"""

from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


# Constants
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()


def configure_login_manager() -> None:
    """Configure Flask-Login settings."""
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"


configure_login_manager()

