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
    # Insert default values if they don't exist
    cursor = conn.cursor()
    for key, value in DEFAULTS.items():
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
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
        # Convert '0'/'1' to boolean for GIST_INPUT
        if key == 'GIST_INPUT':
            return row[0] == '1'
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
    "GIST_INPUT": False,
    "EMAIL_ENABLED": False,
    "FULL_NAME": "Your Name",
    "FILE_NAME": "yourname",
    "WRITER_MODEL": "gpt-4.1",
    "JUDGE_MODEL": "GPT-4.1 mini",
    "AGENT_MODEL": "gpt-4o",
    "EMAIL_FROM": "bot@example.com",
    "EMAIL_TO": "your@email.com",
    "SMTP_SERVER": "smtp.example.com",
    "SMTP_PORT": "465",
    "SMTP_USERNAME": "bot@example.com",
    "SMTP_PASSWORD": "SecretPassword",
    "DB_PATH": DB_PATH,
    "GITHUB_TOKEN": "your_github_token_here",
    "GIST_ID": "your_gist_id_here"
}

# Convenience wrapper to always return *something*
def config(key):
    return get_setting(key, fallback=DEFAULTS.get(key))
