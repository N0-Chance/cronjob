import asyncio
from playwright.async_api import async_playwright
import json
import re
import sqlite3
import os

# Paths
DB_PATH = "db/data.db"

def clean_data(data):
    """Remove empty fields to reduce token usage."""
    if isinstance(data, dict):
        return {k: clean_data(v) for k, v in data.items() if v and v != "unknown"}
    elif isinstance(data, list):
        return [clean_data(v) for v in data if v and v != "unknown"]
    return data

async def scrape_form(url):
    """Scrapes the job posting and form details."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="domcontentloaded")

        # Extract page text
        page_text = await page.evaluate('''() => {
            return document.body.innerText;
        }''')

        # Extract job title
        title = await page.inner_text("h1") if await page.query_selector("h1") else "Unknown"

        # Extract form elements
        form_elements = await page.query_selector_all("input, select, textarea, button")
        extracted_fields = []
        for element in form_elements:
            field_type = await element.get_attribute("type") or "unknown"
            name = await element.get_attribute("name") or await element.get_attribute("id") or "unknown"
            placeholder = await element.get_attribute("placeholder") or ""
            label = await element.inner_text() if await element.inner_text() else ""

            field_data = {
                "type": field_type,
                "name": name,
                "placeholder": placeholder,
                "label": label.strip(),
            }
            if any(field_data.values()) and name != "unknown":
                extracted_fields.append(field_data)

        await browser.close()

        job_data = {"title": title, "description": page_text.strip(), "form_fields": clean_data(extracted_fields)}
        print(f"Scraped job: {title} from {url}")

        return job_data

def update_processing_table(url, job_data):
    """Update the database with scraped job data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE processing SET job_data=?, status='scraped' WHERE url=?", (json.dumps(job_data), url))
    conn.commit()
    conn.close()
    print(f"Updated processing table with scraped job: {url}")

def process_next_job():
    """Move a job from queue to processing and scrape it."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, url FROM queue ORDER BY id ASC LIMIT 1")
    job = cursor.fetchone()

    if not job:
        print("No jobs in queue.")
        conn.close()
        return False

    job_id, job_url = job
    print(f"Processing job: {job_url}")

    # Move job to processing
    cursor.execute("DELETE FROM queue WHERE id=?", (job_id,))
    cursor.execute("INSERT INTO processing (url, status) VALUES (?, 'scraping')", (job_url,))
    conn.commit()
    conn.close()

    # Scrape job
    job_data = asyncio.run(scrape_form(job_url))
    update_processing_table(job_url, job_data)

    return True

if __name__ == "__main__":
    process_next_job()