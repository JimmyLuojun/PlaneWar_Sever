# /Users/junluo/Desktop/桌面文件/PlaneWar_Sever/server/__init__.py
import os
import datetime # <-- Import datetime
from flask import Flask
# --- Ensure this import matches the function defined in config.py ---
from .config import get_config
# --- Import extensions ---
from .extensions import db, migrate, login_manager, bcrypt

def create_app():
    """Application factory function."""
    print("Attempting to create Flask app...") # Debug print
    app = Flask(__name__)

    # --- Load configuration ---
    try:
        config_object = get_config() # Get DevelopmentConfig or ProductionConfig
        app.config.from_object(config_object)
        print(f" * Flask App '{app.name}' created with config: {config_object.__name__}")
        print(f" * Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not Set')}") # Use .get for safety
    except Exception as e:
        print(f"ERROR loading configuration: {e}")
        raise # Re-raise the exception to see the full error

    # --- Initialize extensions ---
    try:
        db.init_app(app)
        migrate.init_app(app, db) # Initialize migrate with app and db
        login_manager.init_app(app)
        bcrypt.init_app(app)
        print(" * Extensions initialized.")
    except Exception as e:
        print(f"ERROR initializing extensions: {e}")
        raise

    # --- Register blueprints ---
    try:
        from .auth import bp as auth_bp
        app.register_blueprint(auth_bp, url_prefix='/auth')

        from .api import bp as api_bp
        app.register_blueprint(api_bp, url_prefix='/api')

        from .views import bp as views_bp
        app.register_blueprint(views_bp) # Register at root URL '/'
        print(" * Blueprints registered.")
    except Exception as e:
        print(f"ERROR registering blueprints: {e}")
        raise

    # --- Add Context Processors --- # <-- NEW SECTION
    @app.context_processor
    def inject_now():
        """Make 'now' available to all templates."""
        return {'now': datetime.datetime.utcnow}
    # --- End Context Processors --- #

    # Optional: Add a simple test route to verify app creation
    @app.route('/_health')
    def health_check():
        return "Server is up!", 200

    print(" * App creation successful.")
    return app
