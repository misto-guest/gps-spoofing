"""
GPS Campaign Manager - Configuration Settings
"""

import os
from pathlib import Path

# ============================================================================
# Base Paths
# ============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent


# ============================================================================
# Database Configuration
# ============================================================================

DATABASE_PATH = BASE_DIR / 'campaigns.db'

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"


def get_db_connection():
    """
    Get database connection

    Returns:
        sqlite3.Connection: Database connection with row factory
    """
    import sqlite3

    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================================
# Flask Configuration
# ============================================================================

SECRET_KEY = os.environ.get('SECRET_KEY', 'gps-campaign-manager-secret-key-change-in-production')

DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

TESTING = False


# ============================================================================
# Server Configuration
# ============================================================================

HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', 5002))


# ============================================================================
# SocketIO Configuration
# ============================================================================

SOCKETIO_CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
SOCKETIO_ASYNC_MODE = 'threading'


# ============================================================================
# Campaign Configuration
# ============================================================================

# Maximum concurrent campaigns
MAX_CONCURRENT_CAMPAIGNS = 5

# Background task intervals
COOLDOWN_CHECK_INTERVAL_SECONDS = 30

# Default campaign settings
DEFAULT_CAMPAIGN_DURATION_HOURS = 1
MAX_CAMPAIGN_DURATION_HOURS = 24
MIN_CAMPAIGN_DURATION_HOURS = 1


# ============================================================================
# Google Account Configuration
# ============================================================================

# Daily trip limits per account
MAX_TRIPS_PER_DAY = 3

# Minimum idle time between trips (hours)
MIN_IDLE_HOURS = 4

# Post-trip cooldown (minutes)
COOLDOWN_MINUTES = 30


# ============================================================================
# Device Configuration
# ============================================================================

# Device sync check interval (seconds)
DEVICE_SYNC_CHECK_INTERVAL = 60

# ADB connection timeout (seconds)
ADB_CONNECTION_TIMEOUT = 10


# ============================================================================
# Logging Configuration
# ============================================================================

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()

LOG_FORMAT = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'

# Log file paths
LOG_DIR = BASE_DIR / 'logs'
LOG_FILE = LOG_DIR / 'gps_campaign_manager.log'

# Ensure log directory exists
LOG_DIR.mkdir(exist_ok=True)


# ============================================================================
# GPS Simulation Configuration
# ============================================================================

# Location update interval (seconds)
GPS_UPDATE_INTERVAL = 2

# Default simulation parameters
DEFAULT_START_LAT = 52.3676
DEFAULT_START_LNG = 4.9041  # Amsterdam

# Account mode presets
ACCOUNT_MODE_PRESETS = {
    'normal': {
        'start_lat': 52.3676,
        'start_lng': 4.9041,  # Amsterdam
        'speed_kmh': 5,
        'radius_km': 0.5
    },
    'aggressive': {
        'start_lat': 51.5074,
        'start_lng': -0.1278,  # London
        'speed_kmh': 15,
        'radius_km': 2.0
    },
    'stealth': {
        'start_lat': 52.3702,
        'start_lng': 4.8952,  # Amsterdam Centrum
        'speed_kmh': 2,
        'radius_km': 0.2
    }
}


# ============================================================================
# Authentication Configuration
# ============================================================================

# JWT settings
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# Password requirements
PASSWORD_MIN_LENGTH = 8


# ============================================================================
# Security Configuration
# ============================================================================

# Rate limiting
RATE_LIMIT_ENABLED = True
RATE_LIMIT_PER_MINUTE = 60

# Session settings
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'


# ============================================================================
# Feature Flags
# ============================================================================

FEATURES = {
    'smart_scheduling': True,
    'google_account_tracking': True,
    'device_registry': True,
    'live_logging': True,
    'stealth_mode': True,
    'multi_user': True
}


# ============================================================================
# Environment Detection
# ============================================================================

def is_production():
    """Check if running in production"""
    return not DEBUG and not TESTING


def is_development():
    """Check if running in development"""
    return DEBUG


def is_testing():
    """Check if running in tests"""
    return TESTING


# ============================================================================
# Validation
# ============================================================================

def validate_config():
    """
    Validate configuration settings

    Raises:
        ValueError: If configuration is invalid
    """
    if MAX_TRIPS_PER_DAY < 1:
        raise ValueError("MAX_TRIPS_PER_DAY must be at least 1")

    if MIN_IDLE_HOURS < 0:
        raise ValueError("MIN_IDLE_HOURS must be non-negative")

    if MAX_CONCURRENT_CAMPAIGNS < 1:
        raise ValueError("MAX_CONCURRENT_CAMPAIGNS must be at least 1")

    if MIN_CAMPAIGN_DURATION_HOURS < 0.5:
        raise ValueError("MIN_CAMPAIGN_DURATION_HOURS must be at least 0.5")

    if MAX_CAMPAIGN_DURATION_HOURS < MIN_CAMPAIGN_DURATION_HOURS:
        raise ValueError("MAX_CAMPAIGN_DURATION_HOURS must be greater than MIN_CAMPAIGN_DURATION_HOURS")


# Run validation on import
validate_config()
