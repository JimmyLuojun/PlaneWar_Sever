"""Flask application factory and local dev entrypoint."""

from datetime import UTC, datetime

from flask import Flask

from .config import get_config
from .infrastructure.extensions import bcrypt, db, login_manager, migrate
from .presentation.routes.api import bp as api_bp
from .presentation.routes.auth import bp as auth_bp
from .presentation.routes.views import bp as views_bp


DEV_HOST = "0.0.0.0"
DEV_PORT = 8000
DEV_DEBUG = True


def create_app(config_class=None, config_override=None):
    """Create and configure the Flask application instance."""
    app = Flask(__name__, template_folder="templates", static_folder="static")

    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)
    if config_override:
        app.config.update(config_override)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(views_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.context_processor
    def inject_current_time():
        return {"now": datetime.now(UTC)}

    @app.shell_context_processor
    def make_shell_context():
        from .data.models import Score, User

        return {"db": db, "User": User, "Score": Score}

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host=DEV_HOST, port=DEV_PORT, debug=DEV_DEBUG)

def run_dev_server() -> None:
    """Convenience entry point to run the development server."""
    app = create_app()
    app.run(host=DEV_HOST, port=DEV_PORT, debug=DEV_DEBUG)
