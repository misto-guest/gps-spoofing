"""
Google Account Model
"""

from datetime import datetime
from typing import Optional


class GoogleAccount:
    """Google account model for tracking trip limits"""

    def __init__(
        self,
        id: str,
        user_id: str,
        account_email: str,
        friendly_name: Optional[str] = None,
        trips_today: int = 0,
        last_trip_time: Optional[datetime] = None,
        last_reset_date: Optional[str] = None,
        created_at: Optional[datetime] = None
    ):
        self.id = id
        self.user_id = user_id
        self.account_email = account_email
        self.friendly_name = friendly_name
        self.trips_today = trips_today
        self.last_trip_time = last_trip_time
        self.last_reset_date = last_reset_date
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'account_email': self.account_email,
            'friendly_name': self.friendly_name,
            'trips_today': self.trips_today,
            'last_trip_time': self.last_trip_time.isoformat() if self.last_trip_time else None,
            'last_reset_date': self.last_reset_date,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    @staticmethod
    def from_row(row) -> 'GoogleAccount':
        """Create GoogleAccount from database row"""
        return GoogleAccount(
            id=row['id'],
            user_id=row['user_id'],
            account_email=row['account_email'],
            friendly_name=row.get('friendly_name'),
            trips_today=row.get('trips_today', 0),
            last_trip_time=datetime.fromisoformat(row['last_trip_time']) if row.get('last_trip_time') else None,
            last_reset_date=row.get('last_reset_date'),
            created_at=datetime.fromisoformat(row['created_at']) if row.get('created_at') else None
        )
