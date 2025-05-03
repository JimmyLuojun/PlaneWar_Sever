# /Users/junluo/Desktop/桌面文件/PlaneWar_Sever/server/__init__.py
from flask import Flask
from .config import get_config # Use the helper function
from .extensions import db, migrate, login_manager, bcrypt
import os

def create_app():
    """Application factory function."""
    app = Flask(__name__)
    config_object = get_config() # Get DevelopmentConfig or ProductionConfig
    app.config.from_object(config_object)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db) # Initialize migrate with app and db
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # Register blueprints
    from .auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from .api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    from .views import bp as views_bp
    app.register_blueprint(views_bp) # Register at root URL '/'

    # Optional: Create database tables if they don't exist during first run in dev
    # Note: It's generally better practice to use `flask db upgrade` for managing the schema.
    # with app.app_context():
    #    db.create_all()

    print(f" * Flask App '{app.name}' created with config: {config_object.__name__}")
    print(f" * Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

    return app