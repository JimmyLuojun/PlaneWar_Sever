"""Main entry point for running the Flask development server.

Imports the application factory (`create_app`) from the server package
and runs the Flask development server when the script is executed directly.
Primarily used for local development and testing.
"""
# server/app.py (or server/__init__.py)

import os
from flask import Flask
# --- Import datetime and UTC ---
from datetime import datetime, UTC #<--- Import datetime object and UTC timezone
from .config import Config, DevelopmentConfig, ProductionConfig # Import your config classes
from .extensions import db, login_manager, bcrypt, migrate # Add migrate if you use it
# --- Import Blueprints ---
from .views import bp as views_bp
from .auth import bp as auth_bp # Assuming you have an auth blueprint
from .api import bp as api_bp
# --- Add other blueprint imports as needed ---

def create_app(config_class=None, config_override=None):
    """
    Application factory function. Creates and configures the Flask application.
    """
    app = Flask(__name__)

    # Determine default config class based on environment if not explicitly passed
    if config_class is None:
        flask_env = os.environ.get('FLASK_ENV', 'production')
        if flask_env == 'development':
            config_class = DevelopmentConfig
        else:
            config_class = ProductionConfig # Default to Production

    # 1. Load configuration from the specified class
    print(f"Loading configuration from: {config_class.__name__}")
    app.config.from_object(config_class)

    # 2. Apply overrides from the dictionary, if provided (for testing)
    if config_override:
        print(f"Applying configuration overrides: {config_override.keys()}")
        app.config.update(config_override) # Updates existing keys or adds new ones

    # --- Initialize Flask Extensions ---
    print("Initializing extensions...")
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    if 'migrate' in locals(): # Initialize migrate only if imported
        migrate.init_app(app, db)
        print("Flask-Migrate initialized.")
    # Initialize other extensions here...
    print("Extensions initialized.")

    # --- Register Blueprints ---
    print("Registering blueprints...")
    app.register_blueprint(views_bp)
    print(f"Registered blueprint: {views_bp.name}")
    # Make sure url_prefix matches usage in url_for and test client calls
    app.register_blueprint(auth_bp, url_prefix='/auth')
    print(f"Registered blueprint: {auth_bp.name} with prefix /auth")
    app.register_blueprint(api_bp, url_prefix='/api')
    print(f"Registered blueprint: {api_bp.name} with prefix /api")
    # Register other blueprints here...
    print("Blueprints registered.")

    # --- Add Context Processor to Inject 'now' ---
    @app.context_processor
    def inject_current_time():
        """Injects the current UTC time object into the template context."""
        # This makes a variable named 'now' available in all templates.
        # It holds the result of datetime.now(UTC).
        return {'now': datetime.now(UTC)}
    # --------------------------------------------

    # Optional: Add other context processors, error handlers, shell context, etc.
    @app.shell_context_processor
    def make_shell_context():
        from .models import User, Score # Import models here for shell context
        return {'db': db, 'User': User, 'Score': Score}

    # Example simple error handler:
    # @app.errorhandler(404)
    # def page_not_found(e):
    #     return render_template('404.html'), 404

    print(f"Flask App '{app.name}' created successfully using {config_class.__name__}.")
    # Print DB URI for verification (mask password if present in real scenarios)
    print(f"Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")

    return app