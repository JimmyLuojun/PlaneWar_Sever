# /Users/junluo/Desktop/桌面文件/PlaneWar_Sever/server/config.py
import os
from dotenv import load_dotenv

# Determine the base directory of the PlaneWar_Server project
# This assumes config.py is in PlaneWar_Server/server/
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# Load the .env file from the base directory
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-hard-to-guess-string'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Default to SQLite in the *instance* folder for Flask
    # Or use the one specified in .env
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'server', 'database.db') # Changed path slightly for clarity

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    # You might want a separate dev database
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
    #    'sqlite:///' + os.path.join(basedir, 'server', 'dev_database.db')

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    # Ensure DATABASE_URL and SECRET_KEY are set securely in the environment
    # e.g., SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # No default SQLite in production!
    if not os.environ.get('DATABASE_URL'):
        raise ValueError("No DATABASE_URL set for production environment")
    if not os.environ.get('SECRET_KEY') or os.environ.get('SECRET_KEY') == 'a-hard-to-guess-string':
         raise ValueError("SECRET_KEY not set or insecure for production environment")

# Helper to get the correct config class based on environment variable
def get_config():
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        return ProductionConfig
    else:
        return DevelopmentConfig