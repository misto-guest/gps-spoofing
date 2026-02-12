# GPS Spoofing Campaign Manager

## 📍 Overview

Complete GPS spoofing automation system for Android devices with campaign management, real-time monitoring, and analytics.

## 🚀 Features

### Core Functionality
- ✅ **Campaign Management**: Create, start, stop, and delete GPS spoofing campaigns
- ✅ **Real-Time Monitoring**: Live progress tracking with Socket.IO
- ✅ **Analytics Dashboard**: Statistics, charts, and campaign insights
- ✅ **Database Storage**: SQLite for persistent campaign data
- ✅ **Web Interface**: Beautiful, responsive dashboard UI
- ✅ **REST API**: Full programmatic access to all features

### Campaign Features
- 📊 **Multiple Account Modes**: Normal, Aggressive, Stealth
- ⏱️ **Flexible Duration**: 1-24 hours with quick-select options
- 📱 **Device Management**: Assign campaigns to specific devices
- 📈 **Progress Tracking**: Real-time progress bars and status updates
- 🔄 **Background Execution**: Non-blocking campaign runs
- 📝 **Logging**: Detailed campaign logs for debugging

## 📱 Android Integration

### Supported Apps
1. **FakeTraveler** (Primary)
   - Package: `com.igork.fakegps`
   - Repository: https://github.com/mcastillof/FakeTraveler
   - License: GPL-3.0
   - No root required

2. **Mock my GPS** (Secondary)
   - Repository: https://github.com/mcastillof/FakeTraveler
   - License: GPL-2.0

## 🛠️ Installation

### Quick Start
```bash
# Clone repository
git clone <repository-url>
cd gps-spoofing

# Install dependencies
pip3 install flask flask-socketio requests

# Run server (choose one)
python3 gps_campaign_manager_v3.py
# OR
cd gps_campaign_manager && python3 run.py
```

### Access Points
- **Dashboard**: http://localhost:5002
- **Create Campaign**: http://localhost:5002/create
- **API Base**: http://localhost:5002/api

## 📚 Documentation

- **GPS-README.md** - Main documentation and API reference
- **GPS-ANDROID-MULTIUSER.md** - Android integration guide
- **GPS-V3-SETUP.md** - v3 setup instructions
- **GPS-IMPLEMENTATION-SUMMARY.md** - Implementation details
- **GPS-ENHANCEMENTS.md** - Feature enhancements

## 🔧 Components

### Python Scripts
- `gps_campaign_manager_v3.py` - Latest standalone version
- `gps_campaign_manager_v2.2.py` - Previous stable version
- `android_gps_controller.py` - Android device control
- `gps_campaign_manager/` - Refactored package structure

### Directory Structure
```
gps-spoofing/
├── gps_campaign_manager/          # Refactored package
│   ├── app/                      # Flask application
│   ├── config.py                 # Configuration
│   └── run.py                    # Entry point
├── gps_campaign_manager_v3.py     # Standalone server
├── android_gps_controller.py       # Android control
└── docs/                         # Documentation files
```

## 📊 API Endpoints

### Dashboard
```bash
GET /api/dashboard/stats        # Statistics
GET /api/dashboard/charts      # Chart data
```

### Campaigns
```bash
POST /api/campaigns            # Create campaign
GET  /api/campaigns/:id        # Get campaign
POST /api/campaigns/:id/start  # Start campaign
POST /api/campaigns/:id/stop   # Stop campaign
```

### Devices
```bash
GET  /api/devices               # List devices
POST /api/devices/register       # Register device
GET  /api/devices/:id           # Device details
```

## 🎯 Quick Start Guide

1. **Start the server**
   ```bash
   python3 gps_campaign_manager_v3.py
   ```

2. **Open dashboard**
   Navigate to http://localhost:5002

3. **Create campaign**
   - Click "➕ Create Campaign"
   - Fill in details (name, device, mode, duration)
   - Click "Create Campaign"

4. **Monitor progress**
   - Real-time updates on dashboard
   - Live progress bars
   - Campaign status tracking

## 🔐 Authentication

Multi-user support with authentication:
- User registration and login
- Session management
- Per-user campaign isolation

## 📈 Analytics

- Total campaigns, completed, running
- Success rate calculation
- Status distribution charts
- Account mode analysis
- 30-day trend tracking
- Duration distribution

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project integrates with open-source GPS spoofing apps licensed under GPL-3.0 and GPL-2.0.

## 🔗 Related Projects

- **FakeTraveler**: https://github.com/mcastillof/FakeTraveler
- **bnbgeeks**: Campaign management platform

## 📞 Support

For issues, questions, or contributions, please open an issue in the repository.
