"""Flask application configuration settings.

Defines configuration classes (e.g., Config, DevelopmentConfig, ProductionConfig)
for different deployment environments. Loads sensitive values from environment
variables and provides default settings.
"""
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
    # Default to SQLite in the *server* directory (can be changed)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(__file__), 'database.db') # Path relative to this file

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    # Example: Use a separate dev database if needed
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
    #    'sqlite:///' + os.path.join(os.path.dirname(__file__), 'dev_database.db')

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    # Ensure DATABASE_URL and SECRET_KEY are set via environment variables for production.
    # The application will likely fail at runtime if they aren't set,
    # which is acceptable for production checks.
    # We removed the immediate 'raise ValueError' checks from here.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') # Rely on environment variable
    SECRET_KEY = os.environ.get('SECRET_KEY') # Rely on environment variable

# Helper to get the correct config class based on environment variable
def get_config():
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        # Add runtime checks here if desired, e.g.:
        # if not ProductionConfig.SQLALCHEMY_DATABASE_URI:
        #     raise ValueError("DATABASE_URL is required for production.")
        # if not ProductionConfig.SECRET_KEY or ProductionConfig.SECRET_KEY == Config.SECRET_KEY:
        #     raise ValueError("SECRET_KEY is required and must be set securely for production.")
        return ProductionConfig
    else:
        return DevelopmentConfig