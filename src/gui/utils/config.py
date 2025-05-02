import os
import sqlite3
from dotenv import load_dotenv
from src.settings import DEFAULTS
import logging

# Motivational quotes (mostly dry wit and stoicism)
QUOTES = [
    "Done is better than perfect. Especially when perfect was never going to happen.",
    "If you're waiting for motivation, you might be waiting forever. Start anyway.",
    "Today’s progress is tomorrow’s momentum.",
    "You don’t have to feel like it. You just have to do it.",
    "The best way out is always through. Especially your inbox.",
    "Tiny progress is still progress. So is opening the damn file.",
    "If it scares you, it might be worth doing. If it annoys you, it’s definitely overdue.",
    "Most success comes from showing up—on time, consistently, and caffeinated.",
    "Nobody’s judging your pace but you. Keep going.",
    "You’re not behind. You’re just in the part of the story where the hero struggles a bit.",
    "Discipline beats inspiration. But caffeine helps both.",
    "You’re allowed to rest. Just don’t quit.",
    "Some days you conquer. Some days you survive. Both count.",
    "Focus on the next step. Not the whole staircase.",
    "Motivation is fleeting. Systems are forever.",
    "You’ve done harder things. This is just another one.",
    "The bar is lower than you think. Step over it.",
    "One day at a time. One checkbox at a time.",
    "Being overwhelmed is okay. Doing nothing is optional.",
    "Perfect is the enemy of submitted.",
    "You don’t need a muse. You need a start time.",
    "Progress doesn’t have to be dramatic. It just has to happen.",
    "If it's stupid but it works, it isn't stupid.",
    "You can’t edit a blank page, but you can complain while typing.",
    "Rejection isn’t failure. It’s redirection. Probably. Hopefully.",
    "The work won’t do itself. You know this. You're reading this instead.",
    "Your future self will thank you. Or sue you. Let’s try for 'thank you.'",
    "Even 10% effort every day compounds. Especially when others are at 0%.",
    "Don’t underestimate what consistent mediocrity can accomplish over time.",
    "Nothing is more motivating than being almost out of options.",
    "You’re not lazy. You’re in energy-saving mode.",
    "You can be tired and still keep going. That’s called being alive.",
    "Some bridges need to be burned. It’s warm. Keep walking.",
    "Don't give up. Even if you're out of snacks.",
    "You're doing fine. Yes, even now.",
    "Keep moving. The doubt can’t hit a moving target.",
    "You can't control outcomes. Just inputs. So input like hell.",
    "The wheel of fortune turns. Try not to be under it.",
    "Be so consistent it's boring. Boring builds empires.",
    "One awkward attempt is better than no attempt at all.",
    "The goal is not to win every day. Just to not quit every day.",
    "Action beats anxiety. Almost every time.",
    "This could be the day it starts to work. You won’t know until you try.",
    "You don’t need to believe in yourself. You just need to behave like you do.",
    "Start now. You can overthink it later.",
    "Write the email. Apply for the job. Click the button. You got this.",
    "You don’t need the mood. You need the motion.",
    "Control what you can. Let go of the rest. Repeat.",
    "Most of what you fear won’t happen. The rest won’t kill you.",
    "Progress is built from boring, repeated acts. Like applying for jobs.",
    "You’re not behind. You’re being forged.",
    "Fortune is indifferent. Be better anyway.",
    "Some things are within your control. Start with those.",
    "Don't argue with reality. Use it.",
    "The obstacle isn't blocking the path — it *is* the path.",
    "Start where you are. It’s the only place you can.",
    "Apathy is easier. Excellence is earned.",
    "Discomfort is data. Don’t run from it. Read it.",
    "Accept everything. Expect nothing. Do your work.",
    "Your feelings don’t define you. Your habits do.",
    "No need to be fearless. Just fear-resistant.",
    "Momentum begins at one action. Not one epiphany.",
    "There is no finish line. Just the next right thing.",
    "Endure. Adapt. Outlast. Repeat.",
    "Nobody cares. That’s freeing. Go do the thing.",
    "You will not be remembered for your excuses.",
    "You’ve survived everything before this. Don’t flinch now.",
    "If it must be done, do it with calm. Or caffeine.",
    "The wheel turns. Stand up and walk anyway.",
    "You are allowed to struggle. You are not allowed to stop.",
    "Mastery is boring. That’s the point.",
    "Let others be loud. Be relentless.",
    "You are not owed ease. You are capable of effort.",
    "Pity won't save you. Perseverance might.",
    "Feel tired. But never helpless.",
    "You were built for more than scrolling.",
    "The world owes you nothing. Create value anyway.",
    "You don’t rise to your goals. You fall to your systems.",
    "Silence the doubt by doing the work.",
    "Be disciplined enough to disappoint your impulses.",
    "Calm is a form of power. Practice it daily.",
    "The reward is not applause. It’s inner peace.",
    "You can't escape hardship. You can become its master.",
    "Time is passing either way. Choose usefulness.",
    "Every act of focus is a rebellion against chaos.",
    "Don’t seek comfort. Seek clarity.",
    "Simplicity. Consistency. Fortitude. That’s it.",
    "Courage isn’t loud. It shows up again tomorrow.",
    "Let go of outcomes. Double down on effort.",
    "You already know what needs doing. Begin.",
    "The grind doesn’t care how you feel. Good. Show it how you act.",
    "Accept the suck. Then transcend it.",
    "Resentment is weakness disguised as wisdom. Let it go.",
    "Fate gets the wheel. You still steer the ship."
]

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
        logging.info("Database initialized and default values inserted.")
        
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
        
        # Insert default values if they don't exist
        for key, value in DEFAULTS.items():
            cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, value))
            logging.info(f"Inserted default value for {key}: {value}")
        
        conn.commit()
        conn.close()
        
    def get(self, key, default=None):
        """Get a setting value, checking both .env and database."""
        # First check environment variables
        # env_value = os.getenv(key)
        # if env_value is not None:
        #     return env_value
            
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
        
        # # Get environment variables first
        # for key in os.environ:
        #     settings[key] = os.getenv(key)
            
        # Then get database settings (overwriting env vars if same key)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT key, value FROM settings")
        for row in cursor.fetchall():
            settings[row[0]] = row[1]
            
        conn.close()
        return settings 