"""Flask application factory and local dev entrypoint.

Creates and configures the Flask app, initializes extensions, registers
blueprints, and provides a small main block for local development.
"""

import os
from datetime import UTC, datetime

from flask import Flask

from .api import bp as api_bp
from .auth import bp as auth_bp
from .config import get_config
from .extensions import bcrypt, db, login_manager, migrate
from .views import bp as views_bp


# Constants
DEV_HOST = "0.0.0.0"
DEV_PORT = 8000
DEV_DEBUG = True


# Core Logic
def create_app(config_class=None, config_override=None):
    """Create and configure the Flask application instance."""
    app = Flask(__name__)

    # Configuration
    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)
    if config_override:
        app.config.update(config_override)

    # Extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    # Blueprints
    app.register_blueprint(views_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(api_bp, url_prefix="/api")

    # Template context
    @app.context_processor
    def inject_current_time():
        return {"now": datetime.now(UTC)}

    # Shell context
    @app.shell_context_processor
    def make_shell_context():
        from .models import User, Score

        return {"db": db, "User": User, "Score": Score}

    return app


# Main
if __name__ == "__main__":
    app = create_app()
    app.run(host=DEV_HOST, port=DEV_PORT, debug=DEV_DEBUG)
