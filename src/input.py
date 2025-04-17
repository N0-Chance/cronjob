import requests
import json
import datetime
import sqlite3
import os
from src.settings import config
import logging

GITHUB_TOKEN = config("GITHUB_TOKEN")
GIST_ID = config("GIST_ID")
GIST_URL = f"https://api.github.com/gists/{GIST_ID}"

# Database path
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "db", "data.db")

# Headers for authentication
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def fetch_job_urls():
    """Fetch job URLs from the Gist, ignoring processed ones."""
    response = requests.get(GIST_URL, headers=HEADERS)
    if response.status_code == 200:
        gist_data = response.json()
        if "cronjob_input.txt" in gist_data["files"]:
            file_content = gist_data["files"]["cronjob_input.txt"]["content"]
            if not file_content.strip():
                print("Gist is empty. No job URLs to process.")
                return []
            return file_content.strip().split("\n")
        else:
            print("Error: File 'cronjob_input.txt' not found in the Gist.")
            return []
    else:
        print("Error fetching Gist:", response.status_code, response.text)
        return []

def update_gist(new_content, updated_count):
    """Update Gist with new content, marking queued jobs."""
    data = {
        "files": {
            "cronjob_input.txt": {"content": new_content}
        }
    }
    response = requests.patch(GIST_URL, headers=HEADERS, data=json.dumps(data))
    if response.status_code == 200 and updated_count > 0:
        print(f"Gist updated with {updated_count} queued jobs.")
    #elif updated_count == 0:
        #print("No new jobs to queue. Gist remains unchanged.")

def is_url_in_database(url):
    """Check if a URL already exists in queue or processing."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM queue WHERE url = ? UNION SELECT 1 FROM processing WHERE url = ?", (url, url))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def insert_into_queue(url):
    """Insert a new job URL into the queue if not already present."""
    if is_url_in_database(url):
        return False  # Already in queue or processing

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO queue (url, status) VALUES (?, 'pending')", (url,))
    conn.commit()
    conn.close()
    return True

def is_url_processed(url):
    """Check if a URL already exists in the processed table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM processed WHERE url = ?", (url,))
    result = cursor.fetchone()
    conn.close()
    return result

def process_jobs():
    """Fetch job URLs, add new ones to the queue, and mark them as queued."""
    #print("process_jobs called")  # Debugging output
    # Check if GIST input is enabled
    gist_input_enabled = bool(int(config("GIST_INPUT")))
    # print(f"GIST_INPUT setting retrieved: {gist_input_enabled}")  # Verify value
    logging.info(f"GIST_INPUT setting: {gist_input_enabled}")
    if not gist_input_enabled:
        # print("GIST input is disabled.")
        return

    # Only fetch job URLs if GIST_INPUT is enabled
    print("Attempting to fetch job URLs...")  # Debugging output
    job_urls = fetch_job_urls()
    if not job_urls:
        # print("No new job URLs found.")
        return

    new_jobs, already_in_queue, marked_done = 0, 0, 0
    updated_urls = []

    for url in job_urls:
        # Track status
        if "[DONE -" in url:
            marked_done += 1
            updated_urls.append(url)
            continue
        if "[QUEUE -" in url:
            already_in_queue += 1
            updated_urls.append(url)
            continue

        # Attempt to add to queue
        if is_url_processed(url):
            processed_id = is_url_processed(url)[0]
            print(f"URL already processed with ID: {processed_id}")
            continue
        if insert_into_queue(url):
            new_jobs += 1
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            updated_urls.append(f"[QUEUE - {timestamp}] {url}")
        else:
            already_in_queue += 1
            updated_urls.append(url)  # Keep original if already in DB

    # Debug output
    print(f"New: {new_jobs} | Already in Queue: {already_in_queue} | Done: {marked_done}")

    # Update Gist with new queued jobs only if needed
    updated_content = "\n".join(updated_urls)
    update_gist(updated_content, new_jobs)

if __name__ == "__main__":
    process_jobs()