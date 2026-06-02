"""
Configuration Management for Voice Assistant
Loads environment variables and provides fallback defaults
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Config:
    """Centralized configuration"""
    
    # Email Settings
    SENDER_EMAIL = os.getenv('SENDER_EMAIL', '')
    SENDER_PASSWORD = os.getenv('SENDER_PASSWORD', '')
    
    # API Keys
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '')
    NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
    
    # Default Values
    DEFAULT_CITY = os.getenv('DEFAULT_CITY', 'Lahore')
    DEFAULT_NEWS_CATEGORY = os.getenv('DEFAULT_NEWS_CATEGORY', 'technology')
    
    # Directories
    HOME_DIR = Path.home()
    DOWNLOADS_DIR = HOME_DIR / "Downloads"
    PROJECTS_DIR = HOME_DIR / "Projects"
    MUSIC_DIR = HOME_DIR / "Music"
    SCREENSHOTS_DIR = HOME_DIR / "Pictures" / "Screenshots"
    
    # TTS Settings
    TTS_RATE = 175
    TTS_VOLUME = 1.0
    
    # Voice Recognition Settings
    RECOGNITION_TIMEOUT = 5
    PHRASE_TIME_LIMIT = 7
    ENERGY_THRESHOLD = 300
    
    @classmethod
    def validate(cls):
        """Check if required configurations are present"""
        warnings = []
        
        if not cls.SENDER_EMAIL:
            warnings.append("⚠️  Email not configured (email features disabled)")
        if not cls.WEATHER_API_KEY:
            warnings.append("⚠️  Weather API key missing (weather features disabled)")
        if not cls.NEWS_API_KEY:
            warnings.append("⚠️  News API key missing (news features disabled)")
        
        return warnings

# Validate on import
config_warnings = Config.validate()
if config_warnings:
    print("\n".join(config_warnings))
    print("💡 Edit .env file to enable all features\n")