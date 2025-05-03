# /Users/junluo/Desktop/桌面文件/PlaneWar_Sever/server/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()

# Tells Flask-Login which view function handles logins (using the blueprint name)
login_manager.login_view = 'auth.login'
# Optional: Customize the message flashed when login is required
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info" # Bootstrap category for styling