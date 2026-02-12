#!/usr/bin/env python3
"""
GPS Campaign Manager v2.2 - Enhanced with Campaign Creation
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import sqlite3
import threading
import logging
from datetime import datetime, timedelta
import uuid
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gps-campaign-manager-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Database setup
DB_PATH = os.path.join(os.path.dirname(__file__), 'campaigns.db')

def init_db():
    """Initialize the database with campaigns table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create campaigns table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS campaigns (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            device_id TEXT,
            account_mode TEXT,
            duration_hours INTEGER,
            status TEXT DEFAULT 'pending',
            current_step TEXT,
            progress REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            error_message TEXT
        )
    ''')

    # Create campaign_logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS campaign_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id TEXT,
            level TEXT,
            message TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (campaign_id) REFERENCES campaigns (id)
        )
    ''')

    conn.commit()
    conn.close()
    logger.info("Database initialized")

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Routes
@app.route('/')
def index():
    """Serve the dashboard"""
    return render_template('dashboard.html')

@app.route('/dashboard')
def dashboard():
    """Serve the dashboard (alias for root)"""
    return render_template('dashboard.html')

@app.route('/create')
def create_campaign_page():
    """Serve the campaign creation page"""
    return render_template('create.html')

# API Routes
@app.route('/api/dashboard/stats')
def get_stats():
    """Get dashboard statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Total campaigns
    cursor.execute('SELECT COUNT(*) as count FROM campaigns')
    total = cursor.fetchone()['count']

    # Completed campaigns
    cursor.execute('SELECT COUNT(*) as count FROM campaigns WHERE status = "completed"')
    completed = cursor.fetchone()['count']

    # Running campaigns
    cursor.execute('SELECT COUNT(*) as count FROM campaigns WHERE status = "running"')
    running = cursor.fetchone()['count']

    # Calculate success rate
    if total > 0:
        success_rate = int((completed / total) * 100)
    else:
        success_rate = 0

    conn.close()
    return jsonify({
        'total_campaigns': total,
        'completed': completed,
        'running': running,
        'success_rate': success_rate
    })

@app.route('/api/dashboard/charts')
def get_charts():
    """Get chart data"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # By status
    cursor.execute('''
        SELECT status, COUNT(*) as count
        FROM campaigns
        GROUP BY status
        ORDER BY count DESC
    ''')
    by_status = [dict(row) for row in cursor.fetchall()]

    # By account mode
    cursor.execute('''
        SELECT account_mode, COUNT(*) as count
        FROM campaigns
        WHERE account_mode IS NOT NULL
        GROUP BY account_mode
        ORDER BY count DESC
    ''')
    by_mode = [dict(row) for row in cursor.fetchall()]

    # Duration distribution
    cursor.execute('''
        SELECT
            CASE
                WHEN duration_hours <= 1 THEN '< 1 hour'
                WHEN duration_hours <= 4 THEN '1-4 hours'
                WHEN duration_hours <= 8 THEN '4-8 hours'
                ELSE '> 8 hours'
            END as range,
            COUNT(*) as count
        FROM campaigns
        GROUP BY range
        ORDER BY MIN(duration_hours)
    ''')
    duration_distribution = [dict(row) for row in cursor.fetchall()]

    # 30-day trend
    cursor.execute('''
        SELECT
            DATE(created_at) as date,
            COUNT(*) as count
        FROM campaigns
        WHERE created_at >= DATE('now', '-30 days')
        GROUP BY DATE(created_at)
        ORDER BY date
    ''')
    trend_30days = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return jsonify({
        'by_status': by_status,
        'by_mode': by_mode,
        'duration_distribution': duration_distribution,
        'trend_30days': trend_30days
    })

@app.route('/api/campaigns/active')
def get_active_campaigns():
    """Get active campaigns"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM campaigns
        WHERE status IN ('pending', 'running')
        ORDER BY created_at DESC
        LIMIT 10
    ''')

    campaigns = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(campaigns)

@app.route('/api/campaigns', methods=['POST'])
def create_campaign():
    """Create a new campaign"""
    try:
        data = request.get_json()

        # Validate required fields
        if not data or not data.get('name'):
            return jsonify({'error': 'Campaign name is required'}), 400

        # Generate campaign ID
        campaign_id = str(uuid.uuid4())[:8]

        # Insert campaign
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO campaigns (
                id, name, device_id, account_mode,
                duration_hours, status, current_step
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            campaign_id,
            data['name'],
            data.get('device_id'),
            data.get('account_mode', 'normal'),
            data.get('duration_hours', 1),
            'pending',
            'Waiting to start...'
        ))

        conn.commit()
        conn.close()

        logger.info(f"Created campaign {campaign_id}: {data['name']}")

        # Emit socket event
        socketio.emit('campaign_created', {
            'campaign_id': campaign_id,
            'name': data['name']
        })

        return jsonify({
            'success': True,
            'campaign_id': campaign_id,
            'message': 'Campaign created successfully'
        }), 201

    except Exception as e:
        logger.error(f"Error creating campaign: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/campaigns/<campaign_id>/start', methods=['POST'])
def start_campaign(campaign_id):
    """Start a campaign"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE campaigns
            SET status = 'running',
                started_at = CURRENT_TIMESTAMP,
                current_step = 'Initializing...'
            WHERE id = ?
        ''', (campaign_id,))

        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Campaign not found'}), 404

        conn.commit()
        conn.close()

        logger.info(f"Started campaign {campaign_id}")

        # Emit socket event
        socketio.emit('campaign_started', {'campaign_id': campaign_id})

        # Start campaign in background thread
        thread = threading.Thread(target=run_campaign, args=(campaign_id,))
        thread.daemon = True
        thread.start()

        return jsonify({'success': True, 'message': 'Campaign started'})

    except Exception as e:
        logger.error(f"Error starting campaign: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/campaigns/<campaign_id>', methods=['DELETE'])
def delete_campaign(campaign_id):
    """Delete a campaign"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM campaigns WHERE id = ?', (campaign_id,))
        cursor.execute('DELETE FROM campaign_logs WHERE campaign_id = ?', (campaign_id,))

        conn.commit()
        conn.close()

        logger.info(f"Deleted campaign {campaign_id}")

        return jsonify({'success': True, 'message': 'Campaign deleted'})

    except Exception as e:
        logger.error(f"Error deleting campaign: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Socket.IO events
@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')
    emit('connect', {'message': 'Connected to GPS Campaign Manager'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')

@socketio.on('refresh_dashboard')
def handle_refresh():
    """Handle dashboard refresh request"""
    emit('dashboard_refreshed', {'message': 'Dashboard refreshed'})

# Campaign execution function
def run_campaign(campaign_id):
    """Run a campaign (simulated for now)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        steps = [
            'Initializing GPS tracking...',
            'Connecting to device...',
            'Starting location tracking...',
            'Monitoring activity...',
            'Collecting data...',
            'Finalizing campaign...',
            'Campaign completed!'
        ]

        for i, step in enumerate(steps):
            # Update progress
            progress = int((i + 1) / len(steps) * 100)

            cursor.execute('''
                UPDATE campaigns
                SET current_step = ?, progress = ?
                WHERE id = ?
            ''', (step, progress, campaign_id))

            conn.commit()

            # Emit socket event
            socketio.emit('campaign_progress', {
                'campaign_id': campaign_id,
                'current_step': step,
                'progress': progress
            })

            # Simulate work
            import time
            time.sleep(2)

        # Mark as completed
        cursor.execute('''
            UPDATE campaigns
            SET status = 'completed',
                completed_at = CURRENT_TIMESTAMP,
                progress = 100
            WHERE id = ?
        ''', (campaign_id,))
        conn.commit()
        conn.close()

        logger.info(f"Campaign {campaign_id} completed")

        # Emit completion event
        socketio.emit('campaign_completed', {
            'campaign_id': campaign_id,
            'status': 'completed'
        })

    except Exception as e:
        logger.error(f"Error running campaign {campaign_id}: {str(e)}")

        # Mark as failed
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE campaigns
            SET status = 'failed',
                error_message = ?
            WHERE id = ?
        ''', (str(e), campaign_id))
        conn.commit()
        conn.close()

if __name__ == '__main__':
    # Initialize database
    init_db()

    # Run the app
    logger.info("Starting GPS Campaign Manager v2.2")
    socketio.run(app, host='0.0.0.0', port=5002, debug=True, allow_unsafe_werkzeug=True)
