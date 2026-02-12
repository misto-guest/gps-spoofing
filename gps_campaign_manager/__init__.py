"""
GPS Campaign Manager v3.2
Multi-user Android GPS spoofing campaign management system
"""

__version__ = '3.2.0'
__author__ = 'GPS Campaign Manager Team'

from config import (
    DATABASE_PATH,
    MAX_CONCURRENT_CAMPAIGNS,
    MAX_TRIPS_PER_DAY,
    MIN_IDLE_HOURS,
    COOLDOWN_MINUTES,
    ACCOUNT_MODE_PRESETS
)

__all__ = [
    '__version__',
    'DATABASE_PATH',
    'MAX_CONCURRENT_CAMPAIGNS',
    'MAX_TRIPS_PER_DAY',
    'MIN_IDLE_HOURS',
    'COOLDOWN_MINUTES',
    'ACCOUNT_MODE_PRESETS',
]
