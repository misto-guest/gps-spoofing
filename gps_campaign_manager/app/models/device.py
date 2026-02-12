"""
Device Model
"""

from datetime import datetime
from typing import Optional
from enum import Enum


class DeviceSyncStatus(Enum):
    """Device sync status"""
    ONLINE = 'online'
    OFFLINE = 'offline'
    ERROR = 'error'


class DeviceScript(Enum):
    """Device script states"""
    NONE = 'none'
    GPS = 'gps'
    CUSTOM = 'custom'


class Device:
    """Device model for Android device registry"""

    def __init__(
        self,
        id: str,
        user_id: str,
        name: str,
        adb_device_id: str,
        proxy_ip: Optional[str] = None,
        current_script: str = 'none',
        sync_status: str = 'offline',
        last_sync: Optional[datetime] = None,
        created_at: Optional[datetime] = None
    ):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.adb_device_id = adb_device_id
        self.proxy_ip = proxy_ip
        self.current_script = current_script
        self.sync_status = sync_status
        self.last_sync = last_sync
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'adb_device_id': self.adb_device_id,
            'proxy_ip': self.proxy_ip,
            'current_script': self.current_script,
            'sync_status': self.sync_status,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    @staticmethod
    def from_row(row) -> 'Device':
        """Create Device from database row"""
        return Device(
            id=row['id'],
            user_id=row['user_id'],
            name=row['name'],
            adb_device_id=row['adb_device_id'],
            proxy_ip=row.get('proxy_ip'),
            current_script=row.get('current_script', 'none'),
            sync_status=row.get('sync_status', 'offline'),
            last_sync=datetime.fromisoformat(row['last_sync']) if row.get('last_sync') else None,
            created_at=datetime.fromisoformat(row['created_at']) if row.get('created_at') else None
        )

    def is_online(self) -> bool:
        """Check if device is online"""
        return self.sync_status == DeviceSyncStatus.ONLINE.value

    def is_busy(self) -> bool:
        """Check if device is running a script"""
        return self.current_script != DeviceScript.NONE.value
