"""
Campaign Model
"""

from datetime import datetime
from typing import Optional
from enum import Enum


class CampaignStatus(Enum):
    """Campaign status enum"""
    QUEUED = 'queued'
    PROCESSING = 'processing'
    COOLDOWN = 'cooldown'
    COMPLETED = 'completed'
    FAILED = 'failed'


class Campaign:
    """Campaign model for GPS tracking campaigns"""

    def __init__(
        self,
        id: str,
        user_id: str,
        name: str,
        device_id: str,
        google_account: Optional[str] = None,
        account_mode: str = 'normal',
        duration_hours: int = 1,
        status: str = 'queued',
        current_step: str = 'Waiting to start...',
        progress: int = 0,
        cooldown_until: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.device_id = device_id
        self.google_account = google_account
        self.account_mode = account_mode
        self.duration_hours = duration_hours
        self.status = status
        self.current_step = current_step
        self.progress = progress
        self.cooldown_until = cooldown_until
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'device_id': self.device_id,
            'google_account': self.google_account,
            'account_mode': self.account_mode,
            'duration_hours': self.duration_hours,
            'status': self.status,
            'current_step': self.current_step,
            'progress': self.progress,
            'cooldown_until': self.cooldown_until.isoformat() if self.cooldown_until else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @staticmethod
    def from_row(row) -> 'Campaign':
        """Create Campaign from database row"""
        return Campaign(
            id=row['id'],
            user_id=row['user_id'],
            name=row['name'],
            device_id=row['device_id'],
            google_account=row.get('google_account'),
            account_mode=row.get('account_mode', 'normal'),
            duration_hours=row['duration_hours'],
            status=row['status'],
            current_step=row.get('current_step', 'Waiting to start...'),
            progress=row.get('progress', 0),
            cooldown_until=datetime.fromisoformat(row['cooldown_until']) if row.get('cooldown_until') else None,
            created_at=datetime.fromisoformat(row['created_at']) if row.get('created_at') else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row.get('updated_at') else None
        )

    def is_active(self) -> bool:
        """Check if campaign is currently active"""
        return self.status in [CampaignStatus.QUEUED.value, CampaignStatus.PROCESSING.value, CampaignStatus.COOLDOWN.value]

    def is_terminal(self) -> bool:
        """Check if campaign is in terminal state"""
        return self.status in [CampaignStatus.COMPLETED.value, CampaignStatus.FAILED.value]

    def can_start(self) -> bool:
        """Check if campaign can be started"""
        return self.status == CampaignStatus.QUEUED.value
