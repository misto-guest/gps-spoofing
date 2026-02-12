"""
User Model
"""

from datetime import datetime
from typing import Optional, List


class User:
    """User model for authentication"""

    def __init__(self, id: str, username: str, email: str, role: str = 'user', created_at: Optional[datetime] = None):
        self.id = id
        self.username = username
        self.email = email
        self.role = role
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    @staticmethod
    def from_row(row) -> 'User':
        """Create User from database row"""
        return User(
            id=row['id'],
            username=row['username'],
            email=row['email'],
            role=row['role'],
            created_at=datetime.fromisoformat(row['created_at']) if row.get('created_at') else None
        )

    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == 'admin'


class UserSettings:
    """User settings model"""

    def __init__(self, user_id: str, key: str, value: str, updated_at: Optional[datetime] = None):
        self.user_id = user_id
        self.key = key
        self.value = value
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'user_id': self.user_id,
            'key': self.key,
            'value': self.value,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
