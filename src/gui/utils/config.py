import os
import sqlite3
from dotenv import load_dotenv

class ConfigManager:
    def __init__(self):
        # Load .env file
        load_dotenv()
        
        # Get database path
        self.db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "db",
            "data.db"
        )
        
        # Ensure database exists
        self.initialize_database()
        
    def initialize_database(self):
        """Create settings table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        
    def get(self, key, default=None):
        """Get a setting value, checking both .env and database."""
        # First check environment variables
        env_value = os.getenv(key)
        if env_value is not None:
            return env_value
            
        # Then check database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return row[0]
        return default
        
    def set(self, key, value):
        """Set a single setting in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value)
        )
        
        conn.commit()
        conn.close()
        
    def save_settings(self, settings_dict):
        """Save multiple settings at once."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for key, value in settings_dict.items():
            cursor.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, value)
            )
            
        conn.commit()
        conn.close()
        
    def get_all_settings(self):
        """Get all settings as a dictionary."""
        settings = {}
        
        # Get environment variables first
        for key in os.environ:
            settings[key] = os.getenv(key)
            
        # Then get database settings (overwriting env vars if same key)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT key, value FROM settings")
        for row in cursor.fetchall():
            settings[row[0]] = row[1]
            
        conn.close()
        return settings 