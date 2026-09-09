"""Application Configuration"""
import os
from datetime import timedelta

class Config:
    """Base configuration"""
"""
Configuration settings for WorkLifeOS
Supports development, testing, and production environments
"""

import os
from datetime import timedelta


class Config:
    """Base configuration"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5000').split(',')
    
    # File Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads/'
    
    # Email
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', True)
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@worklifeos.com')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///worklifeos.db'
    )
    SQLALCHEMY_ECHO = True
    LOG_LEVEL = 'DEBUG'

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_ECHO = False
    LOG_LEVEL = 'WARNING'
    
    # Production security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # Pagination
    ITEMS_PER_PAGE = 20
    
    # Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads')
    
    # Logging
    LOG_LEVEL = 'INFO'


class DevelopmentConfig(Config):
    """Development configuration"""
    
    DEBUG = True
    TESTING = False
    
    # Database - SQLite for development
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///worklifeos_dev.db'
    )
    
    SQLALCHEMY_ECHO = True
    LOG_LEVEL = 'DEBUG'


class TestingConfig(Config):
    """Testing configuration"""
    
    DEBUG = True
    TESTING = True
    
    # Database - In-memory SQLite for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # JWT
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)


class ProductionConfig(Config):
    """Production configuration"""
    
    DEBUG = False
    TESTING = False
    
    # Database - PostgreSQL for production
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://user:password@localhost/worklifeos'
    )
    
    # Enforce HTTPS
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Security headers
    PREFERRED_URL_SCHEME = 'https'
    
    LOG_LEVEL = 'WARNING'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
