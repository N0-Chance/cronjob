import os
import sqlite3
from dotenv import load_dotenv

# === Paths ===
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "db", "data.db")

# === Load .env first ===
load_dotenv()

# === Connect to SQLite ===
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    return conn

# === Core getter ===
def get_setting(key, fallback=None):
    # 1. Check .env (environment variables)
    if key in os.environ:
        return os.getenv(key)

    # 2. Check database (settings stored in SQLite)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return row[0]
    return fallback

# === Core setter ===
def set_setting(key, value):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

# === Optional: preload useful keys ===
DEFAULTS = {
    "WRITER_MODEL": "gpt-4o",
    "JUDGE_MODEL": "gpt-4o",
    "AGENT_MODEL": "gpt-4o",
    "EMAIL_FROM": "bot@example.com",
    "EMAIL_TO": "your@email.com",
    "SMTP_SERVER": "smtp.example.com",
    "SMTP_PORT": "465",
    "SMTP_USERNAME": "bot@example.com",
    "SMTP_PASSWORD": "",
    "DB_PATH": DB_PATH,
    "FILE_NAME": "yourname",
    "FULL_NAME": "Your Name",
}

# Convenience wrapper to always return *something*
def config(key):
    return get_setting(key, fallback=DEFAULTS.get(key))
