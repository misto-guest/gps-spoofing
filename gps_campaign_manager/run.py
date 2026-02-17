#!/usr/bin/env python3
"""
GPS Campaign Manager v3.2 - Refactored
Multi-user Android GPS spoofing campaign management system

Refactored package structure:
- app/models/: Database models
- app/services/: Business logic
- app/routes/: API endpoints
- app/templates/: UI templates
- migrations/: Database migrations
- config.py: Configuration settings
"""

import os
import sys
import logging

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template
from flask_socketio import SocketIO

# Import configuration
from gps_campaign_manager.config import (
    DATABASE_PATH,
    SECRET_KEY,
    DEBUG,
    HOST,
    PORT,
    SOCKETIO_CORS_ALLOWED_ORIGINS,
    SOCKETIO_ASYNC_MODE,
    LOG_LEVEL,
    LOG_FORMAT,
    MAX_CONCURRENT_CAMPAIGNS,
    COOLDOWN_CHECK_INTERVAL_SECONDS
)

# Import migrations
from gps_campaign_manager.migrations import init_database

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DEBUG'] = DEBUG

# Initialize SocketIO
socketio = SocketIO(
    app,
    cors_allowed_origins=SOCKETIO_CORS_ALLOWED_ORIGINS,
    async_mode=SOCKETIO_ASYNC_MODE
)


# ============================================================================
# Database Connection
# ============================================================================

def get_db_connection():
    """Get database connection"""
    from gps_campaign_manager.config import get_db_connection as _get_db_connection
    return _get_db_connection()


# ============================================================================
# Import and Register Routes
# ============================================================================

# Note: In the full refactored version, routes would be imported from app.routes/
# For now, we're keeping the original monolithic gps_campaign_manager_v3.py
# as the main application until all routes are migrated

# Example of how routes would be imported:
# from gps_campaign_manager.app.routes.auth import auth_bp
# from gps_campaign_manager.app.routes.campaigns import campaigns_bp
# from gps_campaign_manager.app.routes.devices import devices_bp
# from gps_campaign_manager.app.routes.google_accounts import google_accounts_bp
# from gps_campaign_manager.app.routes.scheduler import scheduler_bp
#
# app.register_blueprint(auth_bp)
# app.register_blueprint(campaigns_bp)
# app.register_blueprint(devices_bp)
# app.register_blueprint(google_accounts_bp)
# app.register_blueprint(scheduler_bp)


# ============================================================================
# Template Routes
# ============================================================================

@app.route('/')
def index():
    """Dashboard"""
    return render_template('dashboard.html')


@app.route('/login')
def login_page():
    """Login page"""
    return render_template('login.html')


@app.route('/register')
def register_page():
    """Register page"""
    return render_template('register.html')


@app.route('/create')
def create_campaign_page():
    """Create campaign page"""
    return render_template('create.html')


@app.route('/devices')
def devices_page():
    """Devices page"""
    return render_template('devices.html')


@app.route('/history')
def history_page():
    """History page"""
    return render_template('history.html')


# ============================================================================
# Socket.IO Events
# ============================================================================

@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')
    from flask import request
    emit('connected', {'message': 'Connected to GPS Campaign Manager v3.2 (Refactored)'})


@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point"""
    logger.info("Starting GPS Campaign Manager v3.2 (Refactored)")

    # Initialize database
    logger.info(f"Database path: {DATABASE_PATH}")
    init_database(str(DATABASE_PATH))

    # TODO: Initialize service managers
    # from gps_campaign_manager.app.services.auth_manager import AuthManager
    # from gps_campaign_manager.app.services.workflow_manager import CampaignWorkflow
    # from gps_campaign_manager.app.services.device_registry import DeviceRegistry
    # from gps_campaign_manager.app.services.google_account_manager import GoogleAccountManager
    # from gps_campaign_manager.app.services.smart_scheduler import SmartScheduler
    # from gps_campaign_manager.app.services.live_logger import LiveLogger

    # TODO: Start background tasks
    # import threading
    # cooldown_thread = threading.Thread(target=background_cooldown_checker, daemon=True)
    # cooldown_thread.start()

    # Run app
    logger.info(f"Server starting on {HOST}:{PORT}")
    socketio.run(app, host=HOST, port=PORT, debug=DEBUG, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    main()
