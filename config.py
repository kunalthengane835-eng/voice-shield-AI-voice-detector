"""
Configuration file for VoiceShield Backend
"""
import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production-please'
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'ogg', 'flac'}
    DATABASE_PATH = os.environ.get('DATABASE_PATH') or 'database/voiceshield.db'
    
    # JWT settings
    JWT_EXPIRATION_HOURS = 24
    
    # Audio processing settings
    SAMPLE_RATE = 22050
    N_FFT = 2048
    HOP_LENGTH = 512
    
    # AI Detection thresholds
    AI_DETECTION_THRESHOLD = 0.6

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY must be set in production environment")

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
