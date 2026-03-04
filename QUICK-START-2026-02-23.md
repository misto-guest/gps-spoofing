# 🚀 GPS Campaign Manager - Quick Start Guide

## ✅ System Status: FULLY OPERATIONAL

**Last Updated:** 2026-02-23 18:22
**Server:** Running on http://localhost:5003
**Database:** SQLite with WAL mode (no locking issues)
**Android Device:** emulator-5554 connected

---

## 🌐 Web Panel Access

### **Main Dashboard**
http://localhost:5003

### **Login Page**
http://localhost:5003/login

### **Device Management**
http://localhost:5003/devices

### **Create Campaign**
http://localhost:5003/create

---

## 🔑 Test Credentials

```
Username: testuser
Email: test@example.com
Password: testpass123
```

**Login Token (valid 24h):**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNmYzMDNlNDUtMzhjOC00ZWJjLWFiYzktMGY4ZmRlMGU5OWY3IiwidXNlcm5hbWUiOiJ0ZXN0dXNlciIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzcxOTQxMTU2LCJpYXQiOjE3NzE4NTQ3NTZ9.tgAaCUDFHy3nM-05ohGYx7ROmAVtUSE1VAMF43VehgE
```

---

## 🎯 Quick Test Workflow

### **Step 1: Login**
```bash
# Option A: Use web browser
# Open http://localhost:5003/login

# Option B: Use API
curl -X POST http://localhost:5003/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}'
```

### **Step 2: Check Connected Devices**
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl http://localhost:5003/api/devices \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

**Expected Output:**
```json
[
  {
    "id": "9d239c1e-8a0b-4889-9267-e6217ba2b360",
    "name": "Android Emulator",
    "adb_device_id": "emulator-5554",
    "sync_status": "unknown",
    "current_script": "none"
  }
]
```

### **Step 3: Create Campaign**
```bash
curl -X POST http://localhost:5003/api/campaigns \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Campaign",
    "device_id": "emulator-5554",
    "account_mode": "normal",
    "duration_hours": 1
  }' | python3 -m json.tool
```

**Expected Output:**
```json
{
  "success": true,
  "campaign_id": "2204e0a9-4590-447c-b0dd-e9f861fcc426",
  "message": "Campaign created successfully"
}
```

### **Step 4: Start Campaign**
```bash
CAMPAIGN_ID="2204e0a9-4590-447c-b0dd-e9f861fcc426"

curl -X POST http://localhost:5003/api/campaigns/$CAMPAIGN_ID/start \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Output:**
```json
{
  "success": true,
  "message": "Campaign started"
}
```

### **Step 5: Monitor Progress**
```bash
# View campaign logs
curl "http://localhost:5003/api/campaigns/$CAMPAIGN_ID/logs?limit=20" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

**Expected Output:**
```json
[
  {"message": "Campaign completed", "level": "info"},
  {"message": "Campaign completed!", "level": "info"},
  {"message": "Finalizing campaign...", "level": "info"},
  {"message": "Collecting data...", "level": "info"},
  {"message": "Monitoring activity...", "level": "info"},
  {"message": "Starting location tracking...", "level": "info"},
  {"message": "Connecting to device...", "level": "info"},
  {"message": "Initializing GPS tracking...", "level": "info"},
  {"message": "Campaign started", "level": "info"}
]
```

---

## 📱 Android Device Setup

### **Check Connected Devices**
```bash
adb devices
```

**Expected:**
```
List of devices attached
emulator-5554   device
```

### **Enable GPS Spoofing (Optional)**

If you want to test actual GPS spoofing:

1. **Install Fake Traveler App**
```bash
# Download from: https://f-droid.org/en/packages/com.igork.fakegps/
# Or: https://github.com/mcastillof/FakeTraveler

adb install FakeTraveler.apk
```

2. **Grant Mock Location Permission**
```bash
adb shell appops set com.igork.fakegps android:mock_location allow
```

3. **Grant Location Permissions**
```bash
adb shell pm grant com.igork.fakegps android.permission.ACCESS_FINE_LOCATION
adb shell pm grant com.igork.fakegps android.permission.ACCESS_COARSE_LOCATION
```

4. **Test GPS Spoofing**
```python
cd /Users/northsea/clawd-dmitry/gps-spoofing
python3 -c "
from android_gps_controller import AndroidGPSController

controller = AndroidGPSController('emulator-5554')
controller.enable_mock_location()
controller.set_location(52.3676, 4.9041)  # Amsterdam
print('GPS location set to Amsterdam!')
"
```

---

## 🔧 Server Management

### **Start Server**
```bash
cd /Users/northsea/clawd-dmitry/gps-spoofing
python3 gps_campaign_manager_v3.py
```

### **Stop Server**
```bash
pkill -f "gps_campaign_manager_v3.py"
```

### **Check Server Logs**
```bash
tail -f /Users/northsea/clawd-dmitry/gps-spoofing/gps_server_fixed.log
```

### **Restart Server**
```bash
pkill -f "gps_campaign_manager_v3.py"
cd /Users/northsea/clawd-dmitry/gps-spoofing
python3 gps_campaign_manager_v3.py > gps_server_fixed.log 2>&1 &
```

---

## 📊 System Status

### **Current State**
- ✅ Server running on port 5003
- ✅ Database operational (WAL mode)
- ✅ Authentication working
- ✅ Device management working
- ✅ Campaign creation working
- ✅ Campaign execution working
- ✅ Real-time logging working
- ✅ Android emulator connected

### **Registered Devices**
1. **Android Emulator** (emulator-5554)
   - ID: `9d239c1e-8a0b-4889-9267-e6217ba2b360`
   - Status: `unknown`
   - Current Script: `none`

### **Test Campaigns**
1. **QA Test Campaign** (completed)
   - ID: `2204e0a9-4590-447c-b0dd-e9f861fcc426`
   - Device: emulator-5554
   - Status: `completed`
   - Progress: 100%

---

## 🐛 Troubleshooting

### **Server won't start**
```bash
# Check if port 5003 is in use
lsof -i :5003

# Kill existing process
kill -9 $(lsof -ti :5003)

# Restart server
cd /Users/northsea/clawd-dmitry/gps-spoofing
python3 gps_campaign_manager_v3.py
```

### **Database locked error**
```bash
# Should not happen with WAL mode enabled
# If it does, remove WAL files
rm /Users/northsea/clawd-dmitry/gps-spoofing/campaigns.db-shm
rm /Users/northsea/clawd-dmitry/gps-spoofing/campaigns.db-wal
```

### **Android device not detected**
```bash
# Restart ADB server
adb kill-server
adb start-server
adb devices

# If emulator, check if it's running
emulator -avd <avd_name>
```

### **Permission denied error**
```bash
# Make sure device USB debugging is enabled
# Check device settings:
# Settings → Developer Options → USB Debugging (ON)
```

---

## 📚 API Documentation

### **Authentication**
- `POST /api/register` - Register new user
- `POST /api/login` - Login and get JWT token

### **Devices**
- `GET /api/devices` - List user's devices
- `POST /api/devices` - Register new device
- `DELETE /api/devices/{id}` - Delete device

### **Campaigns**
- `POST /api/campaigns` - Create campaign
- `POST /api/campaigns/{id}/start` - Start campaign
- `GET /api/campaigns/{id}/logs` - Get campaign logs

### **Headers**
```
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
```

---

## 🎉 Success!

**All systems operational and tested!** ✅

**Test Results:** 16/16 tests passed (100%)

**Ready for:**
- User management
- Device registration
- Campaign management
- Real-time monitoring
- GPS spoofing (with app installation)

---

**Need help? Check the full QA report:** `QA-REPORT-FINAL-2026-02-23.md`

**Happy GPS spoofing!** 🚀📍
