import os
import sqlite3
import logging
from input import process_jobs as ingest_jobs
from scraper import process_next_job, scrape_form
from writer import process_next_writing_job as process_next_writing_jon
from emailer import check_and_send_emails
from settings import config
import asyncio

# Paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
DB_DIR = os.path.join(ROOT_DIR, "db")
DB_PATH = os.path.join(DB_DIR, "data.db")
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Ensure necessary directories exist
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True)

# Configure logging
LOG_FILE = os.path.join(LOG_DIR, "cronjob.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def initialize_database():
    """Creates database and tables if they don't exist."""
    print(f"Checking database path: {DB_PATH}")  # Debugging output

    # Ensure the db file exists
    if not os.path.exists(DB_PATH):
        print("Database file not found, creating new one...")

    # Connect to SQLite database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE NOT NULL,
        status TEXT DEFAULT 'pending',
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS processing (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE NOT NULL,
        job_title TEXT,
        job_company TEXT,
        degree TEXT,
        degree_reason TEXT,
        job_data JSON,
        resume TEXT,
        resume_pdf TEXT,
        cover_letter TEXT,
        cover_letter_pdf TEXT,
        feedback TEXT,
        status TEXT DEFAULT 'scraping',
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS processed (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE NOT NULL,
        job_title TEXT,
        job_company TEXT,
        degree TEXT,
        degree_reason TEXT,
        job_data JSON,
        resume TEXT,
        resume_pdf TEXT,
        cover_letter TEXT,
        cover_letter_pdf TEXT,
        feedback TEXT,
        status TEXT,
        started_at TIMESTAMP,
        finished_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        emailed, BOOLEAN DEFAULT FALSE
    );
    CREATE TABLE IF NOT EXISTS unable_to_scrape (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE NOT NULL,
        error TEXT,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        job_title TEXT,
        job_company TEXT,
        degree TEXT,
        degree_reason TEXT,
        job_data JSON,
        resume TEXT,
        resume_pdf TEXT,
        cover_letter TEXT,
        cover_letter_pdf TEXT,
        feedback TEXT,
        submission_status TEXT,
        started_at TIMESTAMP          
    );               
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    );

    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

# Job Processing Loop
async def process_queue():
    """Process a job using scraper.py's logic and move only valid ones forward."""
    success = await process_next_job()  # This now handles scraping, failure cases, etc.

    if success:
        logging.info("Successfully scraped a job and moved it forward.")
        return True
    else:
        logging.info("No valid jobs scraped. Waiting for new jobs...")
        return False

# Main Execution Loop
async def main():
    logging.info("Cronjob Pipeline Started.")
    
    # Check and initialize database
    initialize_database()

    while True:
        # Run input processing
        ingest_jobs()

        # Process queued jobs
        job_processed = await process_queue()  # Use await now

        # Run the writer
        process_next_writing_jon()

        # Send emails for completed jobs
        check_and_send_emails()

        if not job_processed:
            logging.info("Waiting before next cycle...")
        
        # Wait before next loop to prevent hammering API/database
        await asyncio.sleep(10)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Cronjob pipeline stopped by keyboard interrupt.")
        print("\nCronjob pipeline stopped by keyboard interrupt.\n")