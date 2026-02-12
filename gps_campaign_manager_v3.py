#!/usr/bin/env python3
"""
GPS Campaign Manager v3.0 - Integrated Server

Combines user authentication, device registry, campaign workflow,
live logging, GPS spoofing simulation, and real-time management.
"""

import os
import uuid
import logging
import math
import time
import threading
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Optional, Tuple

import bcrypt
import jwt
from flask import (
    Flask, jsonify, request, render_template, g
)
from flask_socketio import SocketIO, emit, join_room, leave_room

# === Configuration and Logging ===

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gps_campaign_manager_v3")

SECRET_KEY = "gps-campaign-manager-secret-key-change-in-production"
TOKEN_EXPIRATION_HOURS = 24

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'campaigns.db')

# === Flask and SocketIO setup ===
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
socketio = SocketIO(app, cors_allowed_origins="*")

# === Utility ===
import sqlite3

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# === Authentication Manager ===

class AuthManager:
    def __init__(self):
        pass

    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def generate_token(self, user_id: str, username: str, role: str = 'user') -> str:
        payload = {
            'user_id': user_id,
            'username': username,
            'role': role,
            'exp': datetime.utcnow() + timedelta(hours=TOKEN_EXPIRATION_HOURS),
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return token

    def decode_token(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def register_user(self, username: str, email: str, password: str, role: str = 'user') -> Tuple[bool, str, Optional[str]]:
        if not username or not email or not password:
            return False, "Missing required fields", None
        if len(username) < 3:
            return False, "Username must be at least 3 characters", None
        if len(password) < 6:
            return False, "Password must be at least 6 characters", None
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
        if cursor.fetchone():
            conn.close()
            return False, "Username or email already exists", None
        user_id = str(uuid.uuid4())
        password_hash = self.hash_password(password)
        cursor.execute('''
            INSERT INTO users (id, username, email, password_hash, role)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, email, password_hash, role))
        cursor.execute('INSERT INTO user_settings (user_id) VALUES (?)', (user_id,))
        conn.commit()
        conn.close()
        logger.info(f"New user registered: {username} ({email})")
        return True, "User registered successfully", user_id

    def login_user(self, username: str, password: str) -> Tuple[bool, str, Optional[Dict], Optional[str]]:
        if not username or not password:
            return False, "Missing username or password", None, None
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, username, email, password_hash, role, created_at
            FROM users WHERE username = ? OR email = ?
        ''', (username, username))
        user = cursor.fetchone()
        if not user:
            conn.close()
            return False, "Invalid credentials", None, None
        if not self.verify_password(password, user["password_hash"]):
            conn.close()
            return False, "Invalid credentials", None, None
        cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user["id"],))
        conn.commit()
        conn.close()
        token = self.generate_token(user["id"], user["username"], user["role"])
        user_dict = {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'role': user['role'],
            'created_at': user['created_at']
        }
        logger.info(f"User logged in: {user['username']}")
        return True, "Login successful", user_dict, token

# === Decorators for authentication ===
from functools import wraps
from flask import jsonify

auth_manager = AuthManager()

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header:
            return jsonify({'error': 'No token provided'}), 401
        token = auth_header.replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        payload = auth_manager.decode_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        g.user = payload
        return f(*args, **kwargs)
    return decorated

def require_role(role: str):
    def deco(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = getattr(g, 'user', None)
            if not user or user.get('role') != role:
                return jsonify({'error': 'Forbidden'}), 403
            return f(*args, **kwargs)
        return decorated
    return deco

# === Device Registry ===
class DeviceScript(Enum):
    GPS = "gps"
    MUSIC = "music"
    NONE = "none"

class DeviceSyncStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    UNKNOWN = "unknown"

class DeviceRegistry:
    SYNC_TIMEOUT_SECONDS = 60

    def register_device(self, user_id: str, name: str, adb_device_id: str, proxy_ip: Optional[str] = None, initial_script: str = DeviceScript.NONE.value) -> Tuple[bool, str, Optional[str]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM devices WHERE adb_device_id = ?', (adb_device_id,))
        if cursor.fetchone():
            conn.close()
            return False, "ADB device ID already registered", None
        device_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO devices (id, user_id, name, adb_device_id, proxy_ip, current_script, sync_status, last_sync)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (device_id, user_id, name, adb_device_id, proxy_ip, initial_script, DeviceSyncStatus.UNKNOWN.value, None))
        conn.commit()
        conn.close()
        logger.info(f"Device registered: {name} ({adb_device_id}) by user {user_id}")
        return True, "Device registered successfully", device_id

    def update_device(self, device_id: str, **kwargs) -> Tuple[bool, str]:
        conn = get_db_connection()
        cursor = conn.cursor()
        valid_fields = ['name', 'proxy_ip', 'current_script', 'sync_status', 'last_sync']
        updates = []
        params = []
        for field, value in kwargs.items():
            if field in valid_fields:
                updates.append(f"{field} = ?")
                params.append(value)
        if not updates:
            conn.close()
            return False, "No valid fields to update"
        params.append(device_id)
        query = f"UPDATE devices SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        logger.debug(f"Device {device_id} updated: {kwargs}")
        return True, "Device updated"

    def get_device(self, device_id: str) -> Optional[Dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM devices WHERE id = ?', (device_id,))
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None

    def get_device_by_adb_id(self, adb_device_id: str) -> Optional[Dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM devices WHERE adb_device_id = ?', (adb_device_id,))
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None

    def list_user_devices(self, user_id: str) -> List[Dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM devices WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        devices = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return devices

    def delete_device(self, device_id: str, user_id: str) -> Tuple[bool, str]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM devices WHERE id = ?', (device_id,))
        result = cursor.fetchone()
        if not result:
            conn.close()
            return False, "Device not found"
        if result["user_id"] != user_id:
            conn.close()
            return False, "You don't own this device"
        cursor.execute('''
            SELECT COUNT(*) FROM campaigns WHERE device_id = ? AND status IN ('processing', 'cooldown')
        ''', (device_id,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return False, "Device is currently in use"
        cursor.execute('DELETE FROM devices WHERE id = ?', (device_id,))
        conn.commit()
        conn.close()
        logger.info(f"Device {device_id} deleted by user {user_id}")
        return True, "Device deleted"

    def can_start_gps_campaign(self, device_id: str) -> Tuple[bool, str]:
        device = self.get_device(device_id)
        if not device:
            return False, "Device not found"
        if device.get('current_script') == DeviceScript.MUSIC.value:
            return False, "Device is running Music Script (conflict)"
        if device.get('sync_status') != DeviceSyncStatus.ONLINE.value:
            return False, f"Device is {device.get('sync_status', 'unknown')}"
        return True, "Device available for GPS campaign"

    def set_device_script(self, device_id: str, script_type: str, user_id: str) -> Tuple[bool, str]:
        device = self.get_device(device_id)
        if not device:
            return False, "Device not found"
        if device['user_id'] != user_id:
            return False, "You don't own this device"
        if script_type == DeviceScript.GPS.value:
            can_start, reason = self.can_start_gps_campaign(device_id)
            if not can_start:
                return False, reason
        return self.update_device(device_id, current_script=script_type)

    def update_sync_status(self, adb_device_id: str, status: str) -> Tuple[bool, str]:
        device = self.get_device_by_adb_id(adb_device_id)
        if not device:
            return False, "Device not found in registry"
        now = datetime.now()
        return self.update_device(device['id'], sync_status=status, last_sync=now)

    def check_all_device_sync(self) -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        timeout_time = datetime.now() - timedelta(seconds=self.SYNC_TIMEOUT_SECONDS)
        cursor.execute('''
            UPDATE devices SET sync_status = 'offline'
            WHERE sync_status = 'online' AND last_sync < ?
        ''', (timeout_time,))
        offline_count = cursor.rowcount
        conn.commit()
        conn.close()
        if offline_count > 0:
            logger.info(f"Marked {offline_count} devices as offline (timeout)")
        return offline_count

    def get_available_devices(self, user_id: str) -> List[Dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM devices
            WHERE user_id = ? AND (current_script = 'none' OR current_script = 'gps')
            AND sync_status = 'online'
            ORDER BY name ASC
        ''', (user_id,))
        devices = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return devices

# === Campaign Workflow ===
class CampaignStatus(Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COOLDOWN = "cooldown"
    COMPLETED = "completed"
    FAILED = "failed"

class CampaignWorkflow:
    TRANSITIONS = {
        CampaignStatus.QUEUED: [CampaignStatus.PROCESSING],
        CampaignStatus.PROCESSING: [CampaignStatus.COOLDOWN, CampaignStatus.FAILED],
        CampaignStatus.COOLDOWN: [CampaignStatus.COMPLETED, CampaignStatus.FAILED],
        CampaignStatus.COMPLETED: [],
        CampaignStatus.FAILED: []
    }

    COOLDOWN_MINUTES = 30

    def can_transition(self, current_status: str, new_status: str) -> bool:
        try:
            current = CampaignStatus(current_status)
            new = CampaignStatus(new_status)
            return new in self.TRANSITIONS.get(current, [])
        except ValueError:
            return False

    def transition_status(self, campaign_id: str, new_status: str, error_message: Optional[str] = None) -> Tuple[bool, str]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT status FROM campaigns WHERE id = ?', (campaign_id,))
        result = cursor.fetchone()
        if not result:
            conn.close()
            return False, "Campaign not found"
        current_status = result['status']
        if not self.can_transition(current_status, new_status):
            conn.close()
            return False, f"Invalid transition: {current_status} 12 {new_status}"
        now = datetime.now()
        if new_status == CampaignStatus.PROCESSING.value:
            query = '''
            UPDATE campaigns SET status = ?, queued_at = COALESCE(queued_at, ?), processing_at = ?, current_step = 'Processing...'
            WHERE id = ?
            '''
            params = (new_status, now, now, campaign_id)
        elif new_status == CampaignStatus.COOLDOWN.value:
            cooldown_until = now + timedelta(minutes=self.COOLDOWN_MINUTES)
            query = '''
            UPDATE campaigns SET status = ?, cooldown_until = ?, current_step = 'Cooldown period...'
            WHERE id = ?
            '''
            params = (new_status, cooldown_until, campaign_id)
        elif new_status == CampaignStatus.COMPLETED.value:
            query = '''
            UPDATE campaigns SET status = ?, completed_at = ?, current_step = 'Completed', progress = 100
            WHERE id = ?
            '''
            params = (new_status, now, campaign_id)
        elif new_status == CampaignStatus.FAILED.value:
            query = '''
            UPDATE campaigns SET status = ?, error_message = ?, current_step = 'Failed'
            WHERE id = ?
            '''
            params = (new_status, error_message or 'Unknown error', campaign_id)
        else:
            conn.close()
            return False, f"Unknown status: {new_status}"
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        logger.info(f"Campaign {campaign_id}: {current_status} 12 {new_status}")
        return True, f"Status updated to {new_status}"

    def check_cooldown_complete(self, campaign_id: str) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT cooldown_until FROM campaigns WHERE id = ? AND status = ?', (campaign_id, CampaignStatus.COOLDOWN.value))
        result = cursor.fetchone()
        conn.close()
        if not result or not result['cooldown_until']:
            return False
        cooldown_until = datetime.fromisoformat(result['cooldown_until'])
        return datetime.now() >= cooldown_until

    def auto_advance_cooldown(self, campaign_id: str) -> Tuple[bool, str]:
        if not self.check_cooldown_complete(campaign_id):
            return False, "Cooldown period not complete"
        return self.transition_status(campaign_id, CampaignStatus.COMPLETED.value)

# === Live Logger ===
class LiveLogger:
    def __init__(self):
        pass

    def add_log(self, campaign_id: str, level: str, message: str, device_id: Optional[str] = None) -> bool:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO execution_logs (campaign_id, level, message, device_id, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (campaign_id, level, message, device_id, datetime.now()))
            conn.commit()
            conn.close()
            self.emit_log(campaign_id, level, message, device_id)
            return True
        except Exception as e:
            logger.error(f"Failed to add log: {str(e)}")
            return False

    def emit_log(self, campaign_id: str, level: str, message: str, device_id: Optional[str] = None):
        log_entry = {
            'campaign_id': campaign_id,
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'device_id': device_id
        }
        socketio.emit('log_entry', log_entry, room=f'logs_{campaign_id}')
        logger.debug(f"Emitted log to campaign {campaign_id}: {message}")

    def get_logs(self, campaign_id: str, limit: int = 100, level: Optional[str] = None) -> List[Dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        if level:
            cursor.execute('SELECT * FROM execution_logs WHERE campaign_id = ? AND level = ? ORDER BY timestamp DESC LIMIT ?', (campaign_id, level, limit))
        else:
            cursor.execute('SELECT * FROM execution_logs WHERE campaign_id = ? ORDER BY timestamp DESC LIMIT ?', (campaign_id, limit))
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return logs

# === Location Simulator ===
class LocationSimulator:
    EARTH_RADIUS = 6371

    def __init__(self, controller=None):
        self.controller = controller
        self.running = False

    def calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
        d_lat = lat2 - lat1
        d_lng = lng2 - lng1
        a = math.sin(d_lat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(d_lng/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return self.EARTH_RADIUS * c

    def interpolate_route(self, start_pos: Tuple[float, float], end_pos: Tuple[float, float], num_points: int) -> List[Tuple[float, float]]:
        lat1, lng1 = start_pos
        lat2, lng2 = end_pos
        points = []
        for i in range(num_points + 1):
            ratio = i / num_points
            lat = lat1 + (lat2 - lat1) * ratio
            lng = lng1 + (lng2 - lng1) * ratio
            points.append((lat, lng))
        return points

    def simulate_movement(self, route: List[Tuple[float, float]], speed_kmh: float = 5.0, update_interval: int = 2, progress_callback: Optional[callable] = None) -> bool:
        self.running = True
        total_points = len(route) - 1
        completed_points = 0
        for i in range(len(route) - 1):
            if not self.running:
                break
            start = route[i]
            end = route[i + 1]
            distance = self.calculate_distance(start[0], start[1], end[0], end[1])
            time_hours = distance / speed_kmh if speed_kmh > 0 else 0.5
            time_seconds = time_hours * 3600
            num_updates = max(1, int(time_seconds / update_interval))
            points = self.interpolate_route(start, end, num_updates)
            for point in points:
                if not self.running:
                    break
                success = True
                if self.controller:
                    success = self.controller.set_location(point[0], point[1])
                time.sleep(update_interval)
            completed_points += 1
            progress = int((completed_points / total_points) * 100)
            if progress_callback:
                progress_callback(progress, f"Simulating movement... {progress}%")
        self.running = False
        return True

    def stop(self):
        self.running = False

# === Initialize Database Tables ===

def init_auth_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id TEXT PRIMARY KEY,
            default_account_mode TEXT DEFAULT 'normal',
            default_duration INTEGER DEFAULT 4,
            preferred_device_id TEXT,
            notification_enabled BOOLEAN DEFAULT TRUE,
            timezone TEXT DEFAULT 'UTC',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()


def init_device_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            adb_device_id TEXT UNIQUE NOT NULL,
            proxy_ip TEXT,
            current_script TEXT DEFAULT 'none' CHECK(current_script IN ('gps', 'music', 'none')),
            sync_status TEXT DEFAULT 'unknown' CHECK(sync_status IN ('online', 'offline', 'unknown')),
            last_sync TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()


def init_campaign_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS campaigns (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            device_id TEXT,
            account_mode TEXT,
            duration_hours INTEGER,
            status TEXT DEFAULT 'queued' CHECK(status IN ('queued', 'processing', 'cooldown', 'completed', 'failed')),
            current_step TEXT,
            progress REAL DEFAULT 0,
            queued_at TIMESTAMP,
            processing_at TIMESTAMP,
            cooldown_until TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            error_message TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (device_id) REFERENCES devices(id)
        )
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status)
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS execution_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id TEXT NOT NULL,
            level TEXT NOT NULL CHECK(level IN ('debug', 'info', 'warning', 'error')),
            message TEXT NOT NULL,
            device_id TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (campaign_id) REFERENCES campaigns(id),
            FOREIGN KEY (device_id) REFERENCES devices(id)
        )
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_logs_campaign_timestamp ON execution_logs(campaign_id, timestamp DESC)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_logs_device_timestamp ON execution_logs(device_id, timestamp DESC)
    ''')
    conn.commit()
    conn.close()

# === Instantiate Managers ===

device_registry = DeviceRegistry()
campaign_workflow = CampaignWorkflow()
live_logger = LiveLogger()

# === Flask Routes ===

@app.route('/')
@require_auth
def index():
    return render_template('dashboard.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')
    success, message, user_id = auth_manager.register_user(username, email, password, role)
    status_code = 201 if success else 400
    return jsonify({'success': success, 'message': message, 'user_id': user_id}), status_code

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    success, message, user, token = auth_manager.login_user(username, password)
    if not success:
        return jsonify({'error': message}), 401
    return jsonify({'success': True, 'user': user, 'token': token})

@app.route('/api/devices', methods=['POST'])
@require_auth
def create_device():
    data = request.get_json()
    user_id = g.user['user_id']
    name = data.get('name')
    adb_device_id = data.get('adb_device_id')
    proxy_ip = data.get('proxy_ip')
    success, message, device_id = device_registry.register_device(user_id, name, adb_device_id, proxy_ip)
    status_code = 201 if success else 400
    return jsonify({'success': success, 'message': message, 'device_id': device_id}), status_code

@app.route('/api/devices')
@require_auth
def list_devices():
    user_id = g.user['user_id']
    devices = device_registry.list_user_devices(user_id)
    return jsonify(devices)

@app.route('/api/devices/<device_id>', methods=['DELETE'])
@require_auth
def delete_device(device_id):
    user_id = g.user['user_id']
    success, message = device_registry.delete_device(device_id, user_id)
    status_code = 200 if success else 403
    return jsonify({'success': success, 'message': message}), status_code

@app.route('/api/campaigns', methods=['POST'])
@require_auth
def create_campaign():
    data = request.get_json()
    user_id = g.user['user_id']
    name = data.get('name')
    device_id = data.get('device_id')
    account_mode = data.get('account_mode', 'normal')
    duration_hours = data.get('duration_hours', 1)
    if not name:
        return jsonify({'error': 'Campaign name is required'}), 400
    campaign_id = str(uuid.uuid4())
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO campaigns (id, user_id, name, device_id, account_mode, duration_hours, status, current_step)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (campaign_id, user_id, name, device_id, account_mode, duration_hours, CampaignStatus.QUEUED.value, 'Waiting to start...'))
    conn.commit()
    conn.close()
    socketio.emit('campaign_created', {'campaign_id': campaign_id, 'name': name})
    return jsonify({'success': True, 'campaign_id': campaign_id, 'message': 'Campaign created successfully'}), 201

@app.route('/api/campaigns/<campaign_id>/start', methods=['POST'])
@require_auth
def start_campaign(campaign_id):
    user_id = g.user['user_id']
    # Check ownership and device availability could be added here
    success, msg = campaign_workflow.transition_status(campaign_id, CampaignStatus.PROCESSING.value)
    if not success:
        return jsonify({'error': msg}), 400
    socketio.emit('campaign_started', {'campaign_id': campaign_id})
    # Start campaign background thread
    threading.Thread(target=run_campaign, args=(campaign_id,)).start()
    return jsonify({'success': True, 'message': 'Campaign started'})

@app.route('/api/campaigns/<campaign_id>/logs')
@require_auth
def get_campaign_logs(campaign_id):
    limit = int(request.args.get('limit', 100))
    logs = live_logger.get_logs(campaign_id, limit)
    return jsonify(logs)

@socketio.on('subscribe_logs')
def subscribe_logs(data):
    campaign_id = data.get('campaign_id')
    if campaign_id:
        join_room(f'logs_{campaign_id}')
        logs = live_logger.get_logs(campaign_id, limit=50)
        socketio.emit('log_history', {'campaign_id': campaign_id, 'logs': logs}, room=request.sid)

@socketio.on('unsubscribe_logs')
def unsubscribe_logs(data):
    campaign_id = data.get('campaign_id')
    if campaign_id:
        leave_room(f'logs_{campaign_id}')

# === Core campaign runner ===

def run_campaign(campaign_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM campaigns WHERE id = ?', (campaign_id,))
    campaign = cursor.fetchone()
    if not campaign:
        logger.error(f"Campaign {campaign_id} not found")
        return
    live_logger.add_log(campaign_id, 'info', 'Campaign started')

    steps = [
        'Initializing GPS tracking...'
        , 'Connecting to device...'
        , 'Starting location tracking...'
        , 'Monitoring activity...'
        , 'Collecting data...'
        , 'Finalizing campaign...'
        , 'Campaign completed!'
    ]

    for i, step in enumerate(steps):
        progress = int((i + 1) / len(steps) * 100)
        cursor.execute('UPDATE campaigns SET current_step = ?, progress = ? WHERE id = ?', (step, progress, campaign_id))
        conn.commit()
        live_logger.add_log(campaign_id, 'info', step)
        socketio.emit('campaign_progress', {'campaign_id': campaign_id, 'current_step': step, 'progress': progress})
        time.sleep(2)  # Placeholder for real work

    campaign_workflow.transition_status(campaign_id, CampaignStatus.COMPLETED.value)
    live_logger.add_log(campaign_id, 'info', 'Campaign completed')
    socketio.emit('campaign_completed', {'campaign_id': campaign_id, 'status': 'completed'})
    conn.close()

# === Initialization ===

def init_db():
    init_auth_tables()
    init_device_tables()
    init_campaign_tables()
    logger.info("Initialized all database tables")

if __name__ == '__main__':
    init_db()
    logger.info("Starting GPS Campaign Manager v3.0")
    socketio.run(app, host='0.0.0.0', port=5003, debug=True, allow_unsafe_werkzeug=True)
