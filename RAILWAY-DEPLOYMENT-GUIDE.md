# 🚀 GPS Spoofing Tool - Railway Deployment Guide

**Created:** 2026-03-04
**Repository:** https://github.com/misto-guest/gps-spoofing
**Status:** Ready for Deployment

---

## ⚠️ Railway Deployment Constraints

### **Critical Limitations**

Railway **CANNOT** run the full GPS spoofing functionality because:

1. **No ADB Access** - Railway containers cannot access physical Android devices via ADB
2. **No Device Connection** - Railway is cloud-only, no USB/ADB bridge to phones
3. **Emulator Limitations** - Railway doesn't support Android emulators (requires graphical display)

### **What WILL Work on Railway**

✅ **Web Panel & API**
- User authentication (login/register)
- Campaign management (create, view, edit)
- Device registration
- Campaign logs and history
- Real-time monitoring dashboard

✅ **Database**
- SQLite with persistent volume
- Campaign storage
- User data
- Device records

❌ **What WON'T Work**
- Actual GPS spoofing (requires ADB)
- Device communication (requires physical connection)
- Location tracking (requires Android device)

---

## 🎯 Deployment Strategy

### **Option A: Railway for Web Panel + Local Device Server (RECOMMENDED)**

Split the architecture:
- **Railway:** Web panel, API, database, user management
- **Local Machine:** Device server, ADB communication, GPS spoofing

**Architecture:**
```
User → Railway (Web Panel) → API → Local Device Server (ADB) → Android Phone
```

**Benefits:**
- ✅ Reliable web hosting on Railway
- ✅ Easy access from anywhere
- ✅ Device server runs locally where ADB works
- ✅ Can manage multiple devices from different locations

---

### **Option B: Full Local Deployment**

Run everything locally (not on Railway):
- Web panel, API, database, device server all on one machine
- Direct ADB access to devices
- No cloud hosting

**Benefits:**
- ✅ Full GPS spoofing capability
- ✅ Simple setup
- ✅ No Railway costs

**Drawbacks:**
- ❌ Must be on same network as devices
- ❌ No remote access
- ❌ Machine must stay on

---

## 📋 Option A: Railway Deployment Guide (Hybrid)

### **Step 1: Prepare Railway App**

#### 1.1 Create Railway Project
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create project
railway create gps-spoofing
```

#### 1.2 Create `railway.json` Configuration

Create `/Users/northsea/clawd-dmitry/gps-spoofing/railway.json`:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt",
    "watchPatterns": ["*.py", "gps_campaign_manager/"]
  },
  "deploy": {
    "startCommand": "python gps_campaign_manager_v3.py",
    "healthcheckPath": "/api/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### 1.3 Create `.railway/` Directory Structure

```bash
cd /Users/northsea/clawd-dmitry/gps-spoofing
mkdir -p .railway
```

#### 1.4 Create `nixpacks.toml`

Create `/Users/northsea/clawd-dmitry/gps-spoofing/nixpacks.toml`:

```toml
[phases.build]
cmds = ["pip install -r requirements.txt"]

[start]
cmd = "python gps_campaign_manager_v3.py"

[phases.install]
cmds = ["pip install --upgrade pip"]

[variables]
PORT = "5003"
PYTHONUNBUFFERED = "1"
```

---

### **Step 2: Create Railway Service**

```bash
# Link repository
railway link

# Add Python service
railway add

# Set environment variables
railway variables set PORT=5003
railway variables set PYTHONUNBUFFERED=1
railway variables set RAILWAY_ENVIRONMENT=production
```

---

### **Step 3: Add Persistent Volume**

```bash
# Add volume for SQLite database
railway volume add data

# Or via Railway dashboard:
# Project → Settings → Volumes → Add Volume
# Mount Path: /app/data
```

---

### **Step 4: Modify App for Railway**

#### 4.1 Update `gps_campaign_manager_v3.py`

Add Railway-specific database path:

```python
import os

# Database path configuration
if os.environ.get('RAILWAY_ENVIRONMENT') == 'production':
    # Railway: Use persistent volume
    DB_PATH = '/app/data/campaigns.db'
else:
    # Local: Use current directory
    DB_PATH = 'campaigns.db'

# Update database connection
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
```

#### 4.2 Add Health Check Endpoint

Add to `gps_campaign_manager_v3.py`:

```python
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for Railway"""
    try:
        # Test database connection
        conn = get_db_connection()
        conn.execute('SELECT 1')
        conn.close()

        return jsonify({
            'status': 'healthy',
            'environment': os.environ.get('RAILWAY_ENVIRONMENT', 'development'),
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503
```

---

### **Step 5: Deploy to Railway**

```bash
# Deploy
railway up

# Monitor deployment
railway logs

# Get public URL
railway domain
```

**Expected Output:**
```
Your app is available at: https://gps-spoofing-production.up.railway.app
```

---

### **Step 6: Set Up Local Device Server**

The Railway deployment handles the web panel, but you need a local server for device communication.

#### 6.1 Create Device Server Script

Create `/Users/northsea/clawd-dmitry/gps-spoofing/device_server.py`:

```python
#!/usr/bin/env python3
"""
Local Device Server
Handles ADB communication and GPS spoofing
Receives commands from Railway web panel via webhook
"""

import os
import json
import requests
from flask import Flask, request, jsonify
from android_gps_controller import AndroidGPSController

app = Flask(__name__)

# Configuration
RAILWAY_URL = os.environ.get('RAILWAY_URL', 'http://localhost:5003')
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', 'your-secret-key')

@app.route('/webhook/campaign', methods=['POST'])
def webhook_campaign():
    """Receive campaign start from Railway"""
    data = request.json

    # Verify webhook secret
    if data.get('secret') != WEBHOOK_SECRET:
        return jsonify({'error': 'Unauthorized'}), 401

    campaign_id = data.get('campaign_id')
    device_id = data.get('device_id')
    duration_hours = data.get('duration_hours', 1)

    # Execute campaign locally
    controller = AndroidGPSController(device_id)

    try:
        # Enable mock location
        controller.enable_mock_location()

        # Set location (Amsterdam)
        controller.set_location(52.3676, 4.9041)

        # Wait for duration
        import time
        time.sleep(duration_hours * 3600)

        # Report back to Railway
        requests.post(
            f'{RAILWAY_URL}/api/campaigns/{campaign_id}/complete',
            json={'secret': WEBHOOK_SECRET}
        )

        return jsonify({'status': 'completed'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'healthy', 'devices': ['emulator-5554']})

if __name__ == '__main__':
    app.run(port=5004, debug=True)
```

#### 6.2 Start Device Server

```bash
cd /Users/northsea/clawd-dmitry/gps-spoofing

# Set Railway URL
export RAILWAY_URL="https://gps-spoofing-production.up.railway.app"

# Start device server
python3 device_server.py
```

---

### **Step 7: Configure Railway to Call Local Server**

Add webhook integration to Railway app:

Update `gps_campaign_manager_v3.py` campaign start function:

```python
@app.route('/api/campaigns/<campaign_id>/start', methods=['POST'])
def start_campaign(campaign_id):
    # ... existing code ...

    # Send webhook to local device server
    if os.environ.get('RAILWAY_ENVIRONMENT') == 'production':
        LOCAL_SERVER_URL = os.environ.get('LOCAL_SERVER_URL', 'http://localhost:5004')

        try:
            requests.post(
                f'{LOCAL_SERVER_URL}/webhook/campaign',
                json={
                    'secret': os.environ.get('WEBHOOK_SECRET'),
                    'campaign_id': campaign_id,
                    'device_id': campaign['device_id'],
                    'duration_hours': campaign['duration_hours']
                },
                timeout=5
            )
        except requests.exceptions.RequestException as e:
            # Log error but don't fail (campaign will start when device server is available)
            app.logger.warning(f'Could not reach local device server: {e}')

    return jsonify({'success': True, 'message': 'Campaign started'})
```

Add environment variable on Railway:
```bash
railway variables set LOCAL_SERVER_URL=http://your-local-ip:5004
railway variables set WEBHOOK_SECRET=your-random-secret-key
```

---

## 🔧 Configuration Files Summary

### **Files to Create:**

1. **`railway.json`** - Railway project configuration
2. **`nixpacks.toml`** - Build configuration
3. **`device_server.py`** - Local device communication server
4. **`requirements.txt`** - Python dependencies

### **Files to Modify:**

1. **`gps_campaign_manager_v3.py`**
   - Add Railway database path support
   - Add health check endpoint
   - Add webhook to local device server

---

## 🌐 Architecture Diagram

```
┌─────────────────┐
│   User Browser  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Railway (Cloud)                │
│  - Web Panel                    │
│  - API Endpoints                │
│  - Database (SQLite)            │
│  - Authentication               │
│  - Campaign Management          │
└────────┬────────────────────────┘
         │
         │ Webhook
         ▼
┌─────────────────────────────────┐
│  Local Device Server            │
│  - Receives webhook commands    │
│  - ADB communication            │
│  - GPS spoofing execution       │
└────────┬────────────────────────┘
         │
         │ ADB
         ▼
┌─────────────────────────────────┐
│  Android Phone                  │
│  - GPS spoofing app installed   │
│  - Connected via ADB            │
└────────────────────────────────┘
```

---

## 📝 Railway Environment Variables

Set these in Railway dashboard:

```bash
# Required
PORT=5003
PYTHONUNBUFFERED=1
RAILWAY_ENVIRONMENT=production

# Optional
LOCAL_SERVER_URL=http://your-local-ip:5004
WEBHOOK_SECRET=your-random-secret-key
SECRET_KEY=your-flask-secret-key
```

---

## 🚀 Deployment Checklist

### **Railway (Cloud)**
- [ ] Create Railway project
- [ ] Link GitHub repository
- [ ] Add Python service
- [ ] Configure `nixpacks.toml`
- [ ] Add persistent volume for database
- [ ] Set environment variables
- [ ] Deploy to Railway
- [ ] Verify web panel is accessible
- [ ] Test authentication
- [ ] Test campaign creation

### **Local Device Server**
- [ ] Create `device_server.py`
- [ ] Configure Railway webhook URL
- [ ] Set webhook secret
- [ ] Connect Android device via ADB
- [ ] Start device server
- [ ] Test webhook connection
- [ ] Test GPS spoofing

---

## 🎯 Testing the Deployment

### **Test 1: Railway Web Panel**
```bash
# Access Railway URL
open https://gps-spoofing-production.up.railway.app

# Login with test credentials
# Create a campaign
# Verify it appears in dashboard
```

### **Test 2: Local Device Server**
```bash
# Start device server
python3 device_server.py

# Test health endpoint
curl http://localhost:5004/health
```

### **Test 3: End-to-End**
```bash
# Create campaign on Railway
# Campaign sends webhook to local server
# Local server executes GPS spoofing
# Local server reports back to Railway
# Check campaign status on Railway dashboard
```

---

## 📱 Running on Actual Phones

### **Prerequisites**

1. **Enable Developer Options** on phone:
   - Settings → About Phone → Tap "Build Number" 7 times
   - Settings → Developer Options

2. **Enable USB Debugging**:
   - Settings → Developer Options → USB Debugging (ON)

3. **Install Fake GPS App**:
   - Download from F-Droid: https://f-droid.org/en/packages/com.igork.fakegps/
   - Or install APK directly

4. **Grant Permissions**:
```bash
# Enable mock location
adb shell appops set com.igork.fakegps android:mock_location allow

# Grant location permissions
adb shell pm grant com.igork.fakegps android.permission.ACCESS_FINE_LOCATION
adb shell pm grant com.igork.fakegps android.permission.ACCESS_COARSE_LOCATION
```

### **Connect Phone**

```bash
# Connect phone via USB
adb devices

# Should show your device:
# XXXXXXXX    device

# Register device in web panel
# Use device ID from adb devices
```

### **Run Campaign**

1. Connect phone via ADB
2. Start local device server
3. Create campaign on Railway web panel
4. Campaign executes on phone
5. Monitor logs on Railway dashboard

---

## 🔒 Security Considerations

1. **Webhook Secret** - Use strong random secret for webhook authentication
2. **HTTPS** - Railway provides automatic SSL
3. **Authentication** - JWT tokens already implemented
4. **Firewall** - Local device server should not be exposed to internet
5. **ADB** - Only authorize trusted computers

---

## 💰 Cost Estimate

**Railway:**
- Free tier: $5/month credit
- Expected usage: ~$5-10/month (depends on traffic)

**Local Machine:**
- Free (runs on your existing computer)

**Total:** $5-10/month for cloud web panel + free local execution

---

## 📚 Next Steps

1. ✅ Push code to GitHub (DONE)
2. ⬜ Create Railway project
3. ⬜ Configure deployment files
4. ⬜ Deploy to Railway
5. ⬜ Set up local device server
6. ⬜ Test with Android emulator
7. ⬜ Test with actual phone
8. ⬜ Document setup for users

---

## 🆘 Troubleshooting

### **Railway deployment fails**
- Check logs: `railway logs`
- Verify `nixpacks.toml` syntax
- Check requirements.txt has all dependencies

### **Webhook not reaching local server**
- Verify LOCAL_SERVER_URL is correct
- Check webhook secret matches
- Ensure local server is running
- Check firewall allows connections

### **ADB cannot connect to phone**
- Verify USB debugging is enabled
- Try different USB cable
- Restart ADB: `adb kill-server && adb start-server`
- Authorize computer on phone

---

**End of Railway Deployment Guide**

🚀 Ready to deploy to Railway and test on real phones!
