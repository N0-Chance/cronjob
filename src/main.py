import os
import sqlite3
import logging
import datetime
from input import process_jobs as ingest_jobs
from scraper import scrape_form
from writer import process_next_writing_job as process_next_writing_jon
import asyncio
import json
import openai

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
        JD TEXT,
        JD_reason TEXT,
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
        JD TEXT,
        JD_reason TEXT,
        job_data JSON,
        resume TEXT,
        resume_pdf TEXT,
        cover_letter TEXT,
        cover_letter_pdf TEXT,
        feedback TEXT,
        submission_status TEXT,
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

# Job Processing Loop
async def process_queue():
    """Processes jobs in the queue and moves them to processing."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Fetch the oldest pending job
    cursor.execute("SELECT id, url FROM queue WHERE status='pending' ORDER BY id ASC LIMIT 1")
    job = cursor.fetchone()

    if not job:
        logging.info("No jobs in queue. Waiting for new jobs...")
        conn.close()
        return False

    job_id, job_url = job
    logging.info(f"Processing job: {job_url}")

    # Move job to processing **before** removing from queue
    try:
        cursor.execute("INSERT INTO processing (url, status) VALUES (?, 'scraping')", (job_url,))
        conn.commit()
    except sqlite3.IntegrityError:
        logging.warning(f"Job already in processing: {job_url}")
        conn.close()
        return False  # Stop here if it's already being processed

    # Now remove it from queue
    cursor.execute("DELETE FROM queue WHERE id=?", (job_id,))
    conn.commit()
    conn.close()

    # Run scraper
    try:
        job_data = await scrape_form(job_url)  # Ensure async call is awaited
        full_data = json.dumps(job_data)  # Convert JSON to a string for storage

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE processing SET job_data=?, status='scraped' WHERE url=?",
            (full_data, job_url)
        )
        conn.commit()
        conn.close()
        logging.info(f"Scraped job data for: {job_url}")
    except Exception as e:
        logging.error(f"Error scraping {job_url}: {e}")

    return True

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