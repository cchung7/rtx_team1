"""
Configuration module for CLAP system
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_NAME = os.getenv('DB_NAME', 'clap_db')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # Database URI
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@"
        f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Model Configuration
    MODEL_PATH = os.getenv('MODEL_PATH', 'models/lightgbm_model.pkl')
    DATA_PATH = os.getenv('DATA_PATH', 'data/')
    
    # AQI Categories (EPA Standard)
    AQI_CATEGORIES = {
        'Good': {'range': (0, 50), 'color': '#00E400'},
        'Moderate': {'range': (51, 100), 'color': '#FFFF00'},
        'Unhealthy for Sensitive Groups': {'range': (101, 150), 'color': '#FF7E00'},
        'Unhealthy': {'range': (151, 200), 'color': '#FF0000'},
        'Very Unhealthy': {'range': (201, 300), 'color': '#8F3F97'},
        'Hazardous': {'range': (301, 500), 'color': '#7E0023'}
    }
    
    # Performance Thresholds
    MAX_INGESTION_TIME = 60  # seconds
    MAX_DASHBOARD_RENDER_TIME = 5  # seconds
    RELIABILITY_THRESHOLD = 0.90  # 90% success rate
    AVAILABILITY_TARGET = 0.99  # 99% uptime

