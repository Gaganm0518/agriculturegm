"""
Configuration classes for the Flask application.
Loads environment variables from .env file.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))


class BaseConfig:
    """Base configuration shared across all environments."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-secret-key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'fallback-jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://root:password@localhost/agri_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'pool_size': 10,
        'max_overflow': 20,
    }
    
    # Mail
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME', '')
    
    # Cache / Redis
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Weather API
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '')
    
    # File uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
    REPORTS_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'reports')
    MODELS_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')


class DevelopmentConfig(BaseConfig):
    """Development configuration. Falls back to SQLite if MySQL unavailable."""
    DEBUG = True
    CACHE_TYPE = 'SimpleCache'  # Use simple cache in dev if Redis not available
    
    # Use SQLite for development if MySQL is not available
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(os.path.dirname(os.path.dirname(__file__)), 'agri_dev.db')
    )
    SQLALCHEMY_ENGINE_OPTIONS = {}  # SQLite doesn't support pool options


class ProductionConfig(BaseConfig):
    """Production configuration."""
    DEBUG = False


class TestingConfig(BaseConfig):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ENGINE_OPTIONS = {}  # SQLite doesn't support pool options
    CACHE_TYPE = 'SimpleCache'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=5)


# Config map for easy access
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
}
