"""
Database Schema and Migrations
"""

from datetime import datetime
import sqlite3
import logging

logger = logging.getLogger(__name__)


class DatabaseMigration:
    """Database migration handler"""

    def __init__(self, db_path):
        self.db_path = db_path

    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def run_migrations(self):
        """Run all database migrations"""
        logger.info("Running database migrations...")

        self._create_users_table()
        self._create_user_settings_table()
        self._create_devices_table()
        self._create_campaigns_table()
        self._create_google_accounts_table()
        self._create_campaign_logs_table()
        self._create_execution_logs_table()
        self._create_audit_logs_table()
        self._create_schedule_queue_table()
        self._create_indexes()

        logger.info("Database migrations complete")

    def _create_users_table(self):
        """Create users table"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def _create_user_settings_table(self):
        """Create user_settings table"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, key),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        conn.commit()
        conn.close()

    def _create_devices_table(self):
        """Create devices table"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                adb_device_id TEXT UNIQUE NOT NULL,
                proxy_ip TEXT,
                current_script TEXT DEFAULT 'none',
                sync_status TEXT DEFAULT 'offline',
                last_sync TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        conn.commit()
        conn.close()

    def _create_campaigns_table(self):
        """Create campaigns table"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaigns (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                device_id TEXT NOT NULL,
                google_account TEXT,
                account_mode TEXT DEFAULT 'normal',
                duration_hours INTEGER DEFAULT 1,
                status TEXT DEFAULT 'queued',
                current_step TEXT,
                progress INTEGER DEFAULT 0,
                cooldown_until TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (device_id) REFERENCES devices(id)
            )
        ''')

        conn.commit()
        conn.close()

    def _create_google_accounts_table(self):
        """Create google_accounts table"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS google_accounts (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                account_email TEXT UNIQUE NOT NULL,
                friendly_name TEXT,
                trips_today INTEGER DEFAULT 0,
                last_trip_time TIMESTAMP,
                last_reset_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        conn.commit()
        conn.close()

    def _create_campaign_logs_table(self):
        """Create campaign_logs table"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaign_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id TEXT NOT NULL,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                device_id TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
            )
        ''')

        conn.commit()
        conn.close()

    def _create_execution_logs_table(self):
        """Create execution_logs table"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS execution_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_data TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
            )
        ''')

        conn.commit()
        conn.close()

    def _create_audit_logs_table(self):
        """Create audit_logs table"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                action TEXT NOT NULL,
                resource_type TEXT,
                resource_id TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        conn.commit()
        conn.close()

    def _create_schedule_queue_table(self):
        """Create schedule_queue table"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedule_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id TEXT NOT NULL,
                scheduled_for TIMESTAMP,
                priority INTEGER DEFAULT 0,
                attempts INTEGER DEFAULT 0,
                last_attempt TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
            )
        ''')

        conn.commit()
        conn.close()

    def _create_indexes(self):
        """Create database indexes for performance"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Users indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')

        # Devices indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_devices_user ON devices(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_devices_adb ON devices(adb_device_id)')

        # Campaigns indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_campaigns_user ON campaigns(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_campaigns_device ON campaigns(device_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_campaigns_created ON campaigns(created_at)')

        # Google accounts indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_google_accounts_user ON google_accounts(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_google_accounts_email ON google_accounts(account_email)')

        # Logs indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_campaign_logs_campaign ON campaign_logs(campaign_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_campaign_logs_timestamp ON campaign_logs(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_execution_logs_campaign ON execution_logs(campaign_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp)')

        # Schedule queue indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_queue_scheduled ON schedule_queue(scheduled_for)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_queue_priority ON schedule_queue(priority, created_at)')

        conn.commit()
        conn.close()


def init_database(db_path):
    """
    Initialize database with all tables

    Args:
        db_path: Path to database file
    """
    migration = DatabaseMigration(db_path)
    migration.run_migrations()
