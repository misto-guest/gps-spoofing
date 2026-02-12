# GPS Campaign Manager - Refactored Structure

## Overview

The GPS Campaign Manager has been refactored from a monolithic structure into a clean, maintainable package architecture following best practices for Flask applications.

## New Structure

```
gps_campaign_manager/
├── __init__.py                 # Package initialization
├── config.py                   # Configuration settings
├── run.py                      # Application entry point
│
├── app/                        # Application package
│   ├── __init__.py
│   ├── models/                 # Database models
│   │   ├── __init__.py
│   │   ├── user.py            # User model
│   │   ├── device.py          # Device model
│   │   ├── campaign.py        # Campaign model
│   │   └── google_account.py  # Google Account model
│   │
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── auth_manager.py    # Authentication (to be migrated)
│   │   ├── workflow_manager.py # Campaign workflow (to be migrated)
│   │   ├── device_registry.py # Device management (to be migrated)
│   │   ├── google_account_manager.py # Account tracking (to be migrated)
│   │   ├── smart_scheduler.py # Scheduling logic (to be migrated)
│   │   └── live_logger.py     # Live logging (to be migrated)
│   │
│   ├── routes/                 # API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py            # Auth routes (to be created)
│   │   ├── campaigns.py       # Campaign routes (to be created)
│   │   ├── devices.py         # Device routes (to be created)
│   │   ├── google_accounts.py # Account routes (to be created)
│   │   └── scheduler.py       # Scheduler routes (to be created)
│   │
│   └── templates/              # HTML templates
│       ├── dashboard.html
│       ├── login.html
│       ├── register.html
│       ├── create.html
│       ├── devices.html
│       └── history.html
│
├── migrations/                 # Database migrations
│   ├── __init__.py            # Migration runner
│   └── v1_initial.py          # Initial schema (future)
│
└── tests/                      # Test suite (future)
    ├── __init__.py
    ├── test_models.py
    ├── test_services.py
    └── test_routes.py
```

## Key Improvements

### Before (Monolithic)
- 11 separate Python files in root directory
- Duplicated database connection code
- Mixed concerns (models, services, routes all in one file)
- No clear separation of layers
- Difficult to test individual components
- Hard to navigate and maintain

### After (Refactored)
- ✅ **Clean Package Structure**: Organized by function
- ✅ **Centralized Configuration**: All settings in `config.py`
- ✅ **Proper Models**: ORM-like model classes
- ✅ **Service Layer**: Business logic isolated from routes
- ✅ **Route Blueprints**: Modular API endpoints
- ✅ **Migration System**: Version-controlled database schema
- ✅ **Testable**: Easy to unit test components
- ✅ **Maintainable**: Clear structure, easy to navigate

## Configuration

All configuration is centralized in `config.py`:

```python
from gps_campaign_manager.config import (
    DATABASE_PATH,
    MAX_TRIPS_PER_DAY,
    MIN_IDLE_HOURS,
    COOLDOWN_MINUTES,
    DEBUG,
    HOST,
    PORT
)
```

### Environment Variables

```bash
# Configuration
export SECRET_KEY="your-secret-key"
export DEBUG="False"
export HOST="0.0.0.0"
export PORT="5002"

# Optional
export LOG_LEVEL="INFO"
export CORS_ORIGINS="*"
```

## Running the Application

### Development

```bash
# Using the refactored entry point
cd /Users/northsea/clawd-dmitry
python3 gps_campaign_manager/run.py
```

### Production

```bash
# Set environment variables
export DEBUG="False"
export SECRET_KEY="production-secret-key"

# Run with gunicorn (recommended)
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5002 gps_campaign_manager.run:app
```

## Database Initialization

The refactored version includes a proper migration system:

```python
from gps_campaign_manager.migrations import init_database

# Initialize all tables
init_database('/path/to/campaigns.db')
```

## Model Usage

### User Model

```python
from gps_campaign_manager.app.models.user import User

# Create user
user = User(
    id='123',
    username='john',
    email='john@example.com',
    role='user'
)

# Convert to dict
user_dict = user.to_dict()

# Create from database row
user = User.from_row(db_row)

# Check role
if user.is_admin():
    print("Admin user")
```

### Device Model

```python
from gps_campaign_manager.app.models.device import Device, DeviceSyncStatus

# Create device
device = Device(
    id='123',
    user_id='456',
    name='iPhone 15 Pro',
    adb_device_id='iphone-15-pro',
    sync_status='online'
)

# Check status
if device.is_online():
    print("Device is online")

if device.is_busy():
    print("Device is running a script")
```

### Campaign Model

```python
from gps_campaign_manager.app.models.campaign import Campaign, CampaignStatus

# Create campaign
campaign = Campaign(
    id='123',
    user_id='456',
    name='Downtown Route',
    device_id='789',
    google_account='user@gmail.com',
    status='queued'
)

# Check status
if campaign.can_start():
    print("Ready to start")

if campaign.is_active():
    print("Campaign is active")
```

## Migration Path

### Phase 1: Structure Complete ✅
- [x] Create package structure
- [x] Create models
- [x] Centralize configuration
- [x] Create migration system
- [x] Move templates
- [x] Create entry point

### Phase 2: Service Migration (In Progress)
- [ ] Migrate auth_manager.py → app/services/
- [ ] Migrate campaign_workflow.py → app/services/
- [ ] Migrate device_registry.py → app/services/
- [ ] Migrate google_account_manager.py → app/services/
- [ ] Migrate smart_scheduler.py → app/services/
- [ ] Migrate live_logger.py → app/services/

### Phase 3: Route Migration
- [ ] Extract auth routes from gps_campaign_manager_v3.py
- [ ] Extract campaign routes
- [ ] Extract device routes
- [ ] Extract Google account routes
- [ ] Extract scheduler routes
- [ ] Create route blueprints

### Phase 4: Integration
- [ ] Update all imports
- [ ] Test all endpoints
- [ ] Update database initialization
- [ ] Test background tasks
- [ ] Performance testing

### Phase 5: Cleanup
- [ ] Deprecate old files (keep as backup)
- [ ] Update documentation
- [ ] Create migration guide
- [ ] Add tests

## Benefits of Refactored Structure

### 1. **Easier to Maintain**
- Clear file organization
- Each component has a single responsibility
- Easy to find and update code

### 2. **Better Testing**
- Models can be tested independently
- Services can be mocked
- Routes can be tested with fixtures

### 3. **Scalability**
- Easy to add new features
- Clear extension points
- Modular architecture

### 4. **Team Collaboration**
- Multiple developers can work without conflicts
- Clear ownership of components
- Easier code review

### 5. **Production Ready**
- Proper configuration management
- Migration system for database changes
- Clean separation of concerns

## Backward Compatibility

The original `gps_campaign_manager_v3.py` remains fully functional during migration. The refactored version will run alongside until all components are migrated.

## Next Steps

1. **Complete Service Migration**: Move all service files to `app/services/`
2. **Create Route Blueprints**: Extract routes into separate modules
3. **Add Tests**: Create unit tests for models and services
4. **Update Imports**: Ensure all imports use the new structure
5. **Performance Testing**: Verify no performance regression
6. **Documentation**: Update API documentation

## File Migration Status

| File | Status | New Location |
|------|--------|--------------|
| `auth.py` | Pending | `app/services/auth_manager.py` |
| `campaign_workflow.py` | Pending | `app/services/workflow_manager.py` |
| `device_registry.py` | Pending | `app/services/device_registry.py` |
| `google_account_manager.py` | Pending | `app/services/google_account_manager.py` |
| `smart_scheduler.py` | Pending | `app/services/smart_scheduler.py` |
| `live_logger.py` | Pending | `app/services/live_logger.py` |
| `location_simulator.py` | Pending | `app/services/location_simulator.py` |
| `android_gps_controller.py` | Pending | `app/services/android_gps_controller.py` |
| `stealth_docs.py` | Pending | `app/routes/stealth_docs.py` |
| Templates | ✅ Complete | `app/templates/` |
| Models | ✅ Complete | `app/models/` |

---

**Status**: Phase 1 Complete ✅ | Phase 2-5: Pending

The refactored structure is in place and ready for service migration. The application can run using either the original monolithic version or the new refactored entry point.
