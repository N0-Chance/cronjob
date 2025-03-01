import os
from dotenv import load_dotenv

# Load environment variables from .env if it exists
load_dotenv()

# OpenAI API Key - Can be set in .env or edited here
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")

# Model Selection
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4o")
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.0))

# Hiring Cafe Filters (users can edit directly here)
JOB_FILTERS = {
    "keywords": os.getenv("JOB_KEYWORDS", "contract manager, compliance, remote").split(", "),
    "location": os.getenv("JOB_LOCATION", "USA"),
    "min_salary": int(os.getenv("JOB_MIN_SALARY", 80000))
}

# Browser Automation Settings
BROWSER_OPTIONS = {
    "headless": os.getenv("BROWSER_HEADLESS", "True") == "True",
    "timeout": int(os.getenv("BROWSER_TIMEOUT", 30))
}

# Email Settings
EMAIL_SETTINGS = {
    "enabled": os.getenv("EMAIL_ENABLED", "True") == "True",
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", 587)),
    "sender_email": os.getenv("SENDER_EMAIL", "your-email@gmail.com"),
    "receiver_email": os.getenv("RECEIVER_EMAIL", "your-email@gmail.com")
}

# Token Usage Tracking
TRACK_TOKENS = os.getenv("TRACK_TOKENS", "True") == "True"