import os
import sqlite3
from dotenv import load_dotenv

# === Paths ===
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "db", "data.db")

# === Load .env first ===
load_dotenv()

# === Safe SQLite Connection ===
def get_db_connection():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}")
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
    # 1. Check .env
    if key in os.environ:
        return os.getenv(key)

    # 2. Check database (if available)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = cursor.fetchone()
        conn.close()

        if row:
            if key == 'GIST_INPUT':
                return row[0] == '1'
            return row[0]
    except Exception:
        pass  # Fallback if DB is missing or unreadable

    return fallback

# === Core setter ===
def set_setting(key, value):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        conn.commit()
        conn.close()
    except Exception:
        pass  # Silently fail during setup

# === Optional: preload useful keys ===
DEFAULTS = {
    "GIST_INPUT": False,
    "EMAIL_ENABLED": False,
    "FULL_NAME": "Your Name",
    "FILE_NAME": "yourname",
    "WRITER_MODEL": "gpt-4.1",
    "JUDGE_MODEL": "gpt-4.1-mini",
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

# === Safe wrapper ===
def config(key):
    return get_setting(key, fallback=DEFAULTS.get(key))
