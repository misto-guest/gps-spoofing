# 🚀 GPS Campaign Manager v3.0 - Android Integration + Multi-User

## What's New in v3.0

### 📱 Real Android GPS Spoofing
- **Fake Traveler** integration (com.igork.fakegps)
- **Mock my GPS** support (alternative)
- ADB-based device control
- Real-time location updates
- Route simulation with movement
- Multiple device support

### 👥 Multi-User System
- User registration and login
- JWT token authentication
- Role-based access control (user/admin)
- User-specific campaigns
- Device ownership management
- Audit logging

### 🎯 Enhanced Features
- Device management UI
- User settings and preferences
- Real-time campaign progress with GPS
- Predefined routes
- Campaign templates (coming soon)

---

## Installation

### Prerequisites

1. **Install ADB (Android Debug Bridge)**

```bash
# macOS
brew install android-platform-tools

# Linux (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install android-tools-adb android-tools-fastboot

# Windows
# Download from: https://developer.android.com/studio/releases/platform-tools
```

2. **Install Python Dependencies**

```bash
pip3 install -r requirements-v3.txt
```

3. **Enable USB Debugging on Android Device**

- Go to Settings → About Phone
- Tap "Build Number" 7 times to enable Developer Options
- Go to Settings → Developer Options
- Enable "USB Debugging"
- Connect device via USB and accept debugging prompt

4. **Install GPS Spoofing App**

Install **Fake Traveler** from F-Droid:
- F-Droid: https://f-droid.org/en/packages/com.igork.fakegps/
- Or download APK from: https://github.com/mcastillof/FakeTraveler

```bash
# Install via ADB (if you have APK)
adb install FakeTraveler.apk
```

---

## Quick Start

### 1. Initialize Database

```bash
python3 gps_campaign_manager_v3.py --init-db
```

This creates:
- Users table
- User settings
- Devices table
- Campaigns table (with user_id)
- Audit logs

### 2. Create First User (Admin)

```bash
python3 gps_campaign_manager_v3.py --create-admin \
  --username admin \
  --email admin@example.com \
  --password securepassword
```

Or via API after starting server:

```bash
curl -X POST http://localhost:5002/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "securepassword"
  }'
```

### 3. Start Server

```bash
python3 gps_campaign_manager_v3.py
```

Server runs on: **http://localhost:5002**

### 4. Connect Android Device

```bash
# List connected devices
adb devices

# Should show something like:
# XXXXXXXX    device
```

### 5. Add Device in Dashboard

1. Login at http://localhost:5002/login
2. Go to "Devices" page
3. Click "Add Device"
4. Enter:
   - Name: "My Android Phone"
   - ADB Device ID: XXXXXXXX (from `adb devices`)
   - App Package: `com.igork.fakegps`
5. Click "Connect" to test

### 6. Create Campaign with GPS Spoofing

1. Go to "Create Campaign"
2. Fill in details:
   - Campaign name: "Test GPS Spoofing"
   - Device: Select your device
   - Account mode: Normal
   - Duration: 1 hour
3. Click "Create Campaign"
4. Click "Start" to begin GPS spoofing
5. Watch real-time progress!

---

## API Changes

### Authentication Required

All campaign and device endpoints now require authentication:

```bash
# Login to get token
curl -X POST http://localhost:5002/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "securepassword"
  }'

# Response:
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": "...",
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin"
  }
}

# Use token in subsequent requests
curl -X POST http://localhost:5002/api/campaigns \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -d '{
    "name": "Test Campaign",
    "device_id": "device-123",
    "duration_hours": 1
  }'
```

### New Endpoints

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user

#### Devices
- `GET /api/devices` - List user's devices
- `POST /api/devices` - Add device
- `DELETE /api/devices/<id>` - Delete device
- `POST /api/devices/<id>/connect` - Test connection

#### Campaigns (Enhanced)
- `GET /api/campaigns` - List user's campaigns (filtered by user_id)
- `POST /api/campaigns` - Create campaign (requires auth)
- All campaign operations use user's devices

---

## Account Modes (GPS Behavior)

### Normal Mode
- **Speed:** 5 km/h (walking speed)
- **Route:** Circular movement around start location
- **Radius:** 0.5 km
- **Detection Risk:** Low
- **Best for:** Daily use, standard accounts

### Aggressive Mode
- **Speed:** 15 km/h (cycling speed)
- **Route:** Fast movement between distant points
- **Distance:** 2-5 km
- **Detection Risk:** Medium
- **Best for:** Quick testing, faster results

### Stealth Mode
- **Speed:** 2 km/h (very slow walking)
- **Route:** Small circular pattern
- **Radius:** 0.2 km
- **Detection Risk:** Very Low
- **Best for:** High-value accounts, sensitive operations

---

## Predefined Routes

Available predefined routes:

- **amsterdam_center**: Central Station → Dam Square → Leidseplein → Vondelpark
- **london_center**: Westminster → Camden → Shoreditch → South Bank
- **new_york_center**: Times Square → Empire State → Central Park

Use in campaigns:

```bash
curl -X POST http://localhost:5002/api/campaigns \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "name": "Amsterdam Tour",
    "route_type": "predefined",
    "route_name": "amsterdam_center",
    "duration_hours": 2
  }'
```

---

## Troubleshooting

### ADB Not Found

```bash
# Check if ADB is installed
which adb

# If not found, install it
brew install android-platform-tools  # macOS
sudo apt-get install android-tools-adb  # Linux
```

### Device Not Connected

```bash
# List devices
adb devices

# If empty:
# 1. Check USB cable
# 2. Enable USB debugging on device
# 3. Accept debugging prompt on device
# 4. Try different USB port
```

### Mock Location Not Working

```bash
# Enable mock location for app
adb shell appops set com.igork.fakegps android:mock_location allow

# Check if app is installed
adb shell pm list packages com.igork.fakegps

# Grant permissions
adb shell pm grant com.igork.fakegps android.permission.ACCESS_FINE_LOCATION
adb shell pm grant com.igork.fakegps android.permission.ACCESS_COARSE_LOCATION
```

### Campaign Not Starting

- Check device status in dashboard (must be "available")
- Verify ADB connection (click "Connect" button)
- Check campaign logs in dashboard
- Review server logs: `tail -f server.log`

---

## Security Notes

### Production Deployment

1. **Change JWT Secret**
   ```python
   # In gps_campaign_manager_v3.py
   SECRET_KEY = os.environ.get('JWT_SECRET', 'change-this-in-production')
   ```

2. **Use HTTPS**
   ```bash
   # Setup reverse proxy with nginx
   # Or use Cloudflare tunnel
   cloudflared tunnel --url http://localhost:5002
   ```

3. **Environment Variables**
   ```bash
   export JWT_SECRET="your-super-secret-key"
   export DATABASE_PATH="/var/lib/gps-campaigns.db"
   python3 gps_campaign_manager_v3.py
   ```

4. **Rate Limiting** (coming soon)
   - Implement rate limiting on auth endpoints
   - Add IP-based blocking for brute force protection

---

## Migration from v2.2 to v3.0

### Database Migration

```bash
# Backup existing database
cp campaigns.db campaigns.db.backup

# Run migration script
python3 migrate_v2_to_v3.py
```

This adds:
- `user_id` column to campaigns (defaults to first user)
- New tables: users, user_settings, devices, audit_logs

### Breaking Changes

- All API endpoints now require authentication
- Campaigns are filtered by user
- Devices must be owned by user
- Database schema changed

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Web Browser                          │
│                  (Dashboard UI)                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ JWT Token
                     │
┌────────────────────▼────────────────────────────────────┐
│              Flask + SocketIO Server                    │
│                      │                                  │
│    ┌─────────────────┼─────────────────┐               │
│    │                 │                 │               │
│ ┌──▼────┐       ┌────▼───┐       ┌────▼───┐           │
│ │  Auth  │       │Campaign│       │Device  │           │
│ │Manager│       │ Manager│       │Manager │           │
│ └──┬────┘       └────┬───┘       └────┬───┘           │
└────┼────────────────┼────────────────┼────────────────┘
    │                │                │
    ▼                ▼                ▼
┌─────────┐    ┌──────────┐    ┌──────────┐
│  Users  │    │Campaigns │    │ Devices  │
└─────────┘    └──────────┘    └──────────┘
                                  │
                                  │ ADB
                                  ▼
                           ┌──────────┐
                           │ Android  │
                           │  Device  │
                           └──────────┘
```

---

## Next Steps

1. **Test Basic Setup**
   - Install ADB
   - Connect device
   - Install Fake Traveler
   - Test GPS spoofing manually

2. **Deploy Server**
   - Initialize database
   - Create admin user
   - Start server
   - Test authentication

3. **Add Devices**
   - Register Android devices
   - Test ADB connection
   - Verify mock location works

4. **Run Campaigns**
   - Create test campaign
   - Start GPS spoofing
   - Monitor progress
   - Verify location changes

---

## Support

For issues or questions:
- Check troubleshooting section above
- Review ADB logs: `adb logcat`
- Check server logs in terminal
- Verify device connection: `adb devices`

---

**Ready for real GPS spoofing with multi-user support!** 🚀
