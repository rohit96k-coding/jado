import sqlite3
import os
import config
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        self.db_path = os.path.join(config.DATA_DIR, "sami_memory.db")
        self._create_tables()

    def _get_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _create_tables(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Key-Value Store for Settings (User Profile, Preferences)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    category TEXT,
                    key TEXT,
                    value TEXT,
                    PRIMARY KEY (category, key)
                )
            """)
            
            # Conversation History
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT,
                    content TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()

    def upsert_setting(self, category, key, value):
        """Insert or Update a setting."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO settings (category, key, value)
                VALUES (?, ?, ?)
            """, (category, key, str(value)))
            conn.commit()

    def get_setting(self, category, key):
        """Retrieve a specific setting."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE category = ? AND key = ?", (category, key))
            row = cursor.fetchone()
            return row[0] if row else None

    def get_all_settings(self, category):
        """Retrieve all settings for a category as a dict."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM settings WHERE category = ?", (category,))
            rows = cursor.fetchall()
            return {row[0]: row[1] for row in rows}

    def add_history(self, role, content):
        """Add a conversation turn."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO history (role, content) VALUES (?, ?)", (role, content))
            conn.commit()
            
            # Maintenance: Keep only last 50 entries to prevent infinite growth (optional for now, but good practice)
            # cursor.execute("DELETE FROM history WHERE id NOT IN (SELECT id FROM history ORDER BY id DESC LIMIT 50)")
            # conn.commit()

    def get_history(self, limit=5):
        """Get the last N history items."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT role, content FROM history ORDER BY id DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            # Return reversed so it is chronological
            return [{"role": row[0], "content": row[1]} for row in reversed(rows)]
