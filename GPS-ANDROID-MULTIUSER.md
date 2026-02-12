# 🚀 GPS Campaign Manager - Android Integration + Multi-User Support

## Executive Summary

This document outlines the implementation of **real Android GPS spoofing** via open-source apps and **multi-user support** with authentication.

---

## 📱 Part 1: Android GPS Spoofing Integration

### Target Apps

#### 1. Fake Traveler (Primary)
- **Package**: `com.igork.fakegps`
- **License**: GPL-3.0 (Open Source)
- **Method**: Android Mock Location API (no root needed)
- **Features**:
  - Set fake location
  - Simulate movement over time
  - Configurable speed and route
  - F-Droid + GitHub available
- **Source**: https://github.com/mcastillof/FakeTraveler

#### 2. Mock my GPS (Secondary)
- **Package**: `com.example.mockgps` (to be verified)
- **License**: GPL-2.0
- **Features**:
  - Mock GPS and network provider
  - Trip simulation between locations
  - Timing configuration
  - Regularly updated
- **Source**: https://github.com/mcastillof/FakeTraveler

### Integration Methods

#### Method A: ADB (Android Debug Bridge) - Recommended
**Pros:**
- ✅ Full programmatic control
- ✅ No app modification needed
- ✅ Works with any mock location app
- ✅ Can automate everything

**Implementation:**
```bash
# Enable mock location app
adb shell appops set com.igork.fakegps android:mock_location allow

# Set location via intent (Fake Traveler)
adb shell am start -n com.igork.fakegps/.MainActivity \
  --es latitude "52.3676" \
  --es longitude "4.9041" \
  --ez start_mock true

# Or use broadcast to send coordinates
adb shell am broadcast -a com.igork.fakegps.SET_LOCATION \
  --es lat "52.3676" \
  --es lng "4.9041"
```

#### Method B: App Intents (Direct Control)
**Pros:**
- ✅ Faster execution
- ✅ Less overhead than ADB
- ✅ More reliable for frequent updates

**Implementation:**
```python
import subprocess
import json

class AndroidGPSController:
    """Control Android GPS spoofing apps"""

    def __init__(self, device_id=None):
        self.device_id = device_id

    def set_location(self, lat, lng, app_package="com.igork.fakegps"):
        """Set GPS location on Android device"""
        cmd = [
            "adb",
            f"-s {self.device_id}" if self.device_id else "",
            "shell", "am", "broadcast",
            "-a", f"{app_package}.SET_LOCATION",
            "--es", "lat", str(lat),
            "--es", "lng", str(lng)
        ]

        result = subprocess.run(
            " ".join(cmd),
            shell=True,
            capture_output=True,
            text=True
        )

        return result.returncode == 0

    def start_mocking(self, app_package="com.igork.fakegps"):
        """Start location mocking"""
        cmd = [
            "adb",
            f"-s {self.device_id}" if self.device_id else "",
            "shell", "am", "start",
            "-n", f"{app_package}/.MainActivity",
            "--ez", "start_mock", "true"
        ]

        result = subprocess.run(
            " ".join(cmd),
            shell=True,
            capture_output=True,
            text=True
        )

        return result.returncode == 0

    def stop_mocking(self, app_package="com.igork.fakegps"):
        """Stop location mocking"""
        cmd = [
            "adb",
            f"-s {self.device_id}" if self.device_id else "",
            "shell", "am", "broadcast",
            "-a", f"{app_package}.STOP_MOCK"
        ]

        result = subprocess.run(
            " ".join(cmd),
            shell=True,
            capture_output=True,
            text=True
        )

        return result.returncode == 0

    def set_route(self, coordinates, speed_kmh=5, app_package="com.igork.fakegps"):
        """Set route for movement simulation"""
        # Convert coordinates to JSON
        route_json = json.dumps(coordinates)

        cmd = [
            "adb",
            f"-s {self.device_id}" if self.device_id else "",
            "shell", "am", "broadcast",
            "-a", f"{app_package}.SET_ROUTE",
            "--es", "route", route_json,
            "--es", "speed", str(speed_kmh)
        ]

        result = subprocess.run(
            " ".join(cmd),
            shell=True,
            capture_output=True,
            text=True
        )

        return result.returncode == 0

    def get_device_location(self):
        """Get current device location (for verification)"""
        cmd = [
            "adb",
            f"-s {self.device_id}" if self.device_id else "",
            "shell", "dumpsys", "location"
        ]

        result = subprocess.run(
            " ".join(cmd),
            shell=True,
            capture_output=True,
            text=True
        )

        # Parse output to extract location
        # (implementation depends on output format)
        return result.stdout

    def list_connected_devices(self):
        """List all connected Android devices"""
        cmd = ["adb", "devices"]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        lines = result.stdout.strip().split('\n')[1:]
        devices = []

        for line in lines:
            if line.strip():
                parts = line.split('\t')
                if len(parts) >= 2:
                    devices.append({
                        'id': parts[0],
                        'status': parts[1]
                    })

        return devices
```

### Location Simulation Logic

```python
import math
import time
from datetime import datetime, timedelta

class LocationSimulator:
    """Simulate GPS movement along a route"""

    EARTH_RADIUS = 6371  # km

    def __init__(self, controller: AndroidGPSController):
        self.controller = controller
        self.running = False

    def calculate_bearing(self, lat1, lng1, lat2, lng2):
        """Calculate bearing between two points"""
        lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
        d_lng = lng2 - lng1

        y = math.sin(d_lng) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - \
            math.sin(lat1) * math.cos(lat2) * math.cos(d_lng)

        bearing = math.atan2(y, x)
        return (math.degrees(bearing) + 360) % 360

    def calculate_distance(self, lat1, lng1, lat2, lng2):
        """Calculate distance between two points (Haversine formula)"""
        lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])

        d_lat = lat2 - lat1
        d_lng = lng2 - lng1

        a = math.sin(d_lat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(d_lng/2)**2
        c = 2 * math.asin(math.sqrt(a))

        return self.EARTH_RADIUS * c

    def interpolate_route(self, start_pos, end_pos, num_points):
        """Generate intermediate points between two locations"""
        lat1, lng1 = start_pos
        lat2, lng2 = end_pos

        points = []

        for i in range(num_points + 1):
            ratio = i / num_points
            lat = lat1 + (lat2 - lat1) * ratio
            lng = lng1 + (lng2 - lng1) * ratio
            points.append((lat, lng))

        return points

    def simulate_movement(self, route, speed_kmh=5, update_interval=2):
        """
        Simulate movement along a route

        Args:
            route: List of (lat, lng) tuples
            speed_kmh: Speed in km/h
            update_interval: Seconds between location updates
        """
        self.running = True

        for i in range(len(route) - 1):
            if not self.running:
                break

            start = route[i]
            end = route[i + 1]

            # Calculate distance and time
            distance = self.calculate_distance(
                start[0], start[1],
                end[0], end[1]
            )

            # Time = distance / speed (in hours)
            time_hours = distance / speed_kmh
            time_seconds = time_hours * 3600

            # Number of updates for this segment
            num_updates = max(1, int(time_seconds / update_interval))

            # Generate intermediate points
            points = self.interpolate_route(start, end, num_updates)

            # Send location updates
            for point in points:
                if not self.running:
                    break

                self.controller.set_location(point[0], point[1])
                time.sleep(update_interval)

        return True

    def stop(self):
        """Stop simulation"""
        self.running = False
```

### Campaign Execution with Real GPS Spoofing

```python
def run_campaign_with_gps(campaign_id, android_controller):
    """
    Run a campaign with real Android GPS spoofing
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get campaign details
        cursor.execute('''
            SELECT * FROM campaigns WHERE id = ?
        ''', (campaign_id,))

        campaign = dict(cursor.fetchone())

        # Define campaign steps
        steps = [
            'Initializing GPS controller...',
            'Connecting to Android device...',
            'Starting location spoofing...',
            'Simulating movement...',
            'Monitoring activity...',
            'Collecting location data...',
            'Finalizing campaign...'
        ]

        # Initialize location simulator
        simulator = LocationSimulator(android_controller)

        # Execute steps
        for i, step in enumerate(steps):
            if not campaign['status'] == 'running':
                break

            progress = int((i + 1) / len(steps) * 100)

            cursor.execute('''
                UPDATE campaigns
                SET current_step = ?, progress = ?
                WHERE id = ?
            ''', (step, progress, campaign_id))
            conn.commit()

            socketio.emit('campaign_progress', {
                'campaign_id': campaign_id,
                'current_step': step,
                'progress': progress
            })

            # Execute GPS operations
            if 'Connecting to Android device' in step:
                devices = android_controller.list_connected_devices()
                if not devices:
                    raise Exception("No Android devices connected")

            elif 'Starting location spoofing' in step:
                # Start location mocking based on account mode
                if campaign['account_mode'] == 'normal':
                    start_lat, start_lng = 52.3676, 4.9041  # Amsterdam
                elif campaign['account_mode'] == 'aggressive':
                    start_lat, start_lng = 51.5074, -0.1278  # London
                else:  # stealth
                    start_lat, start_lng = 52.3702, 4.8952  # Amsterdam Centrum

                android_controller.start_mocking()
                android_controller.set_location(start_lat, start_lng)

            elif 'Simulating movement' in step:
                # Generate a route based on account mode
                if campaign['account_mode'] == 'normal':
                    # Normal: 5km/h, 1 hour movement
                    end_lat, end_lng = 52.3900, 4.9000
                    speed = 5
                elif campaign['account_mode'] == 'aggressive':
                    # Aggressive: 15km/h, 30 min movement
                    end_lat, end_lng = 51.5300, -0.1000
                    speed = 15
                else:  # stealth
                    # Stealth: 2km/h, 2 hour movement
                    end_lat, end_lng = 52.3750, 4.8950
                    speed = 2

                # Generate route
                num_points = int(campaign['duration_hours'] * 60 / 2)  # 2-min intervals
                route = simulator.interpolate_route(
                    (start_lat, start_lng),
                    (end_lat, end_lng),
                    num_points
                )

                # Simulate movement
                simulator.simulate_movement(route, speed_kmh=speed)

            elif 'Finalizing campaign' in step:
                # Stop mocking
                android_controller.stop_mocking()

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

        socketio.emit('campaign_completed', {
            'campaign_id': campaign_id,
            'status': 'completed'
        })

        logger.info(f"Campaign {campaign_id} completed with GPS spoofing")

    except Exception as e:
        logger.error(f"Error running campaign {campaign_id}: {str(e)}")

        # Stop GPS spoofing
        try:
            android_controller.stop_mocking()
        except:
            pass

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
```

---

## 👥 Part 2: Multi-User Support

### Database Schema Changes

```sql
-- Users table
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- User settings
CREATE TABLE user_settings (
    user_id TEXT PRIMARY KEY,
    default_account_mode TEXT DEFAULT 'normal',
    default_duration INTEGER DEFAULT 4,
    preferred_device_id TEXT,
    notification_enabled BOOLEAN DEFAULT TRUE,
    timezone TEXT DEFAULT 'UTC',
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Add user_id to campaigns
ALTER TABLE campaigns ADD COLUMN user_id TEXT;
ALTER TABLE campaigns ADD COLUMN is_public BOOLEAN DEFAULT FALSE;

-- Create indexes
CREATE INDEX idx_campaigns_user_id ON campaigns(user_id);
CREATE INDEX idx_campaigns_status ON campaigns(status);
CREATE INDEX idx_users_username ON users(username);

-- Devices table (multi-device support)
CREATE TABLE devices (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    name TEXT NOT NULL,
    device_id TEXT UNIQUE NOT NULL,  -- ADB device ID
    app_package TEXT DEFAULT 'com.igork.fakegps',
    status TEXT DEFAULT 'available',  -- available, in_use, offline
    last_used TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Audit logs
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    action TEXT NOT NULL,
    resource_type TEXT,
    resource_id TEXT,
    ip_address TEXT,
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Authentication System

```python
import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify

SECRET_KEY = "your-secret-key-change-in-production"

def generate_token(user_id, username, role='user'):
    """Generate JWT token"""
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def decode_token(token):
    """Decode JWT token"""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def hash_password(password):
    """Hash password with bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def require_auth(f):
    """Authentication decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')

        if not token:
            return jsonify({'error': 'No token provided'}), 401

        payload = decode_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401

        request.user = payload
        return f(*args, **kwargs)

    return decorated_function

def require_role(role):
    """Role-based access control decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'user'):
                return jsonify({'error': 'Authentication required'}), 401

            if role == 'admin' and request.user.get('role') != 'admin':
                return jsonify({'error': 'Admin access required'}), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

### User Management Endpoints

```python
# User registration
@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.get_json()

        # Validate input
        if not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing required fields'}), 400

        # Check if user exists
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?',
                      (data['username'], data['email']))

        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Username or email already exists'}), 409

        # Create user
        user_id = str(uuid.uuid4())
        password_hash = hash_password(data['password'])

        cursor.execute('''
            INSERT INTO users (id, username, email, password_hash)
            VALUES (?, ?, ?, ?)
        ''', (user_id, data['username'], data['email'], password_hash))

        # Create default settings
        cursor.execute('''
            INSERT INTO user_settings (user_id)
            VALUES (?)
        ''', (user_id,))

        conn.commit()
        conn.close()

        logger.info(f"New user registered: {data['username']}")

        return jsonify({
            'success': True,
            'message': 'User registered successfully'
        }), 201

    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# User login
@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()

        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Missing username or password'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, username, email, password_hash, role
            FROM users WHERE username = ?
        ''', (data['username'],))

        user = cursor.fetchone()
        conn.close()

        if not user or not verify_password(data['password'], user['password_hash']):
            return jsonify({'error': 'Invalid credentials'}), 401

        # Update last login
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?',
                      (user['id'],))
        conn.commit()
        conn.close()

        # Generate token
        token = generate_token(user['id'], user['username'], user['role'])

        logger.info(f"User logged in: {user['username']}")

        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role']
            }
        })

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Get current user
@app.route('/api/auth/me')
@require_auth
def get_current_user():
    """Get current user info"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, username, email, role, created_at, last_login
        FROM users WHERE id = ?
    ''', (request.user['user_id'],))

    user = cursor.fetchone()
    conn.close()

    return jsonify({
        'id': user['id'],
        'username': user['username'],
        'email': user['email'],
        'role': user['role'],
        'created_at': user['created_at'],
        'last_login': user['last_login']
    })

# Update campaign endpoints to use user_id
@app.route('/api/campaigns', methods=['POST'])
@require_auth
def create_campaign():
    """Create a new campaign (authenticated)"""
    try:
        data = request.get_json()

        campaign_id = str(uuid.uuid4())[:8]

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO campaigns (
                id, name, device_id, account_mode,
                duration_hours, status, current_step, user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            campaign_id,
            data['name'],
            data.get('device_id'),
            data.get('account_mode', 'normal'),
            data.get('duration_hours', 1),
            'pending',
            'Waiting to start...',
            request.user['user_id']
        ))

        conn.commit()
        conn.close()

        # Log action
        log_audit_action(request.user['user_id'], 'create_campaign', 'campaign', campaign_id)

        socketio.emit('campaign_created', {
            'campaign_id': campaign_id,
            'name': data['name'],
            'user_id': request.user['user_id']
        })

        return jsonify({
            'success': True,
            'campaign_id': campaign_id,
            'message': 'Campaign created successfully'
        }), 201

    except Exception as e:
        logger.error(f"Error creating campaign: {str(e)}")
        return jsonify({'error': str(e)}), 500

def log_audit_action(user_id, action, resource_type, resource_id):
    """Log audit action"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO audit_logs (user_id, action, resource_type, resource_id, ip_address, user_agent)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        action,
        resource_type,
        resource_id,
        request.remote_addr,
        str(request.user_agent)
    ))

    conn.commit()
    conn.close()
```

### Device Management Endpoints

```python
@app.route('/api/devices', methods=['GET'])
@require_auth
def list_devices():
    """List user's devices"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM devices
        WHERE user_id = ?
        ORDER BY created_at DESC
    ''', (request.user['user_id'],))

    devices = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(devices)

@app.route('/api/devices', methods=['POST'])
@require_auth
def add_device():
    """Add new device"""
    try:
        data = request.get_json()

        device_id = str(uuid.uuid4())

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO devices (id, user_id, name, device_id, app_package)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            device_id,
            request.user['user_id'],
            data['name'],
            data['adb_device_id'],
            data.get('app_package', 'com.igork.fakegps')
        ))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'device_id': device_id,
            'message': 'Device added successfully'
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices/<device_id>/connect', methods=['POST'])
@require_auth
def connect_device(device_id):
    """Test connection to device"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM devices WHERE id = ? AND user_id = ?
    ''', (device_id, request.user['user_id']))

    device = cursor.fetchone()
    conn.close()

    if not device:
        return jsonify({'error': 'Device not found'}), 404

    # Test ADB connection
    controller = AndroidGPSController(device['device_id'])
    devices = controller.list_connected_devices()

    found = any(d['id'] == device['device_id'] for d in devices)

    if found:
        # Update status
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE devices SET status = ? WHERE id = ?',
                      ('available', device_id))
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'status': 'connected'})
    else:
        return jsonify({'error': 'Device not connected via ADB'}), 404
```

---

## 🎯 Implementation Plan

### Phase 1: Android Integration (Week 1)
- [ ] Install and configure ADB
- [ ] Install Fake Traveler on test device
- [ ] Implement `AndroidGPSController` class
- [ ] Test basic location spoofing
- [ ] Implement `LocationSimulator` class
- [ ] Test route simulation

### Phase 2: Multi-User Authentication (Week 2)
- [ ] Update database schema
- [ ] Implement user registration
- [ ] Implement JWT authentication
- [ ] Add authentication decorators
- [ ] Create login page UI

### Phase 3: Device Management (Week 3)
- [ ] Create devices table
- [ ] Implement device CRUD endpoints
- [ ] Add device connection testing
- [ ] Create device management UI

### Phase 4: Campaign Integration (Week 4)
- [ ] Update campaign creation to use devices
- [ ] Integrate GPS spoofing in campaign execution
- [ ] Add user-specific campaign filtering
- [ ] Update dashboard for multi-user

### Phase 5: Testing & Deployment (Week 5)
- [ ] End-to-end testing
- [ ] Load testing with multiple users
- [ ] Security audit
- [ ] Production deployment

---

## 📦 Dependencies

Add to `requirements.txt`:
```
Flask>=2.0.0
Flask-SocketIO>=5.0.0
PyJWT>=2.4.0
bcrypt>=4.0.0
```

ADB setup:
```bash
# macOS
brew install android-platform-tools

# Linux
sudo apt-get install android-tools-adb

# Verify
adb devices
```

---

## 🔒 Security Considerations

1. **JWT Secret**: Use environment variable in production
2. **Password Hashing**: bcrypt with appropriate work factor
3. **ADB Security**: Limit ADB access to trusted networks
4. **Rate Limiting**: Implement on auth endpoints
5. **Input Validation**: Validate all user inputs
6. **HTTPS**: Required for production

---

## 📊 Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  User 1      │     │  User 2      │     │  User N      │
│  (Browser)   │     │  (Browser)   │     │  (Browser)   │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                     │                     │
       └─────────────────────┼─────────────────────┘
                            │
                ┌───────────▼──────────┐
                │  Flask + SocketIO    │
                │  (JWT Auth)          │
                └───────────┬──────────┘
                            │
       ┌────────────────────┼────────────────────┐
       │                    │                    │
┌──────▼──────┐     ┌──────▼──────┐     ┌──────▼──────┐
│  Campaign 1 │     │  Campaign 2 │     │  Campaign N │
│  (User 1)   │     │  (User 2)   │     │  (User N)   │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                     │                     │
       └─────────────────────┼─────────────────────┘
                            │
                ┌───────────▼──────────┐
                │  AndroidGPSController│
                │  (ADB Bridge)        │
                └───────────┬──────────┘
                            │
       ┌────────────────────┼────────────────────┐
       │                    │                    │
┌──────▼──────┐     ┌──────▼──────┐     ┌──────┐
│  Device 1   │     │  Device 2   │     │ Dev N│
│  (Android)  │     │  (Android)  │     │      │
└─────────────┘     └─────────────┘     └──────┘
```

---

## ✅ Success Metrics

- [ ] Support 100+ concurrent users
- [ ] Real-time GPS spoofing on Android devices
- [ ] < 2s latency for location updates
- [ ] 99.9% authentication success rate
- [ ] Zero data leakage between users
- [ ] Audit log for all actions

---

**Ready to implement!** 🚀
