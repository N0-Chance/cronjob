from playwright.async_api import async_playwright
import json
import sqlite3

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
        # Launch browser
        browser = await p.chromium.launch(headless=True)

        # Use a real browser user-agent to reduce bot detection
        real_user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

        context = await browser.new_context(
            java_script_enabled=True,
            user_agent=real_user_agent
        )

        page = await context.new_page()

        # Try loading the page with an extended timeout
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)  # Increased timeout to 30s
        except Exception as e:
            print(f"Error loading page: {e}")
            await browser.close()
            return {
                "title": "",
                "description": "",
                "form_fields": [],
                "error": str(e)
            }

        # Click "Accept Cookies" only if it exists
        accept_button = await page.query_selector("button#accept-recommended-btn-handler, button:has-text('Accept All')")
        if accept_button:
            is_visible = await accept_button.is_visible()
            if is_visible:
                await accept_button.click()
                await page.wait_for_timeout(2000)  # Wait for page update after clicking
            else:
                print("Accept button found, but not visible. Skipping click.")

        # Click "Read More" only if it exists
        read_more_button = await page.query_selector("button:has-text('Read More'), button:has-text('Show More')")
        if read_more_button:
            await read_more_button.click()
            await page.wait_for_timeout(2000)

        # Extract job title from multiple selectors
        possible_title_selectors = ["h1", "h2", ".jobTitle", "div.job-header > span", "div.job-title"]
        title = "Unknown"
        for selector in possible_title_selectors:
            elt = await page.query_selector(selector)
            if elt:
                temp_title = (await elt.inner_text()).strip()
                if temp_title:
                    title = temp_title
                    break

        # Extract job description
        description_selectors = ["div.job-description", "section[data-automation-id='jobDescription']", "#jobDescriptionText", "article"]
        page_text = ""
        for sel in description_selectors:
            desc_element = await page.query_selector(sel)
            if desc_element:
                page_text = (await desc_element.inner_text()).strip()
                if page_text:
                    break

        # Fallback: Use full page text if no description is found
        if not page_text:
            page_text = await page.evaluate("() => document.body.innerText")
        
        # Detect cloud block or fake content
        if "access to this page is restricted" in page_text.lower():
            return {
                "title": "Blocked",
                "description": page_text.strip(),
                "form_fields": [],
                "error": "Cloud protection block page"
            }

        # Extract form fields
        form_elements = await page.query_selector_all("input, select, textarea, button")
        extracted_fields = []
        for element in form_elements:
            field_type = await element.get_attribute("type") or "unknown"
            name = await element.get_attribute("name") or await element.get_attribute("id") or "unknown"
            placeholder = await element.get_attribute("placeholder") or ""
            label_text = (await element.inner_text()) or ""
            field_data = {"type": field_type, "name": name, "placeholder": placeholder, "label": label_text.strip()}
            if any(field_data.values()) and name != "unknown":
                extracted_fields.append(field_data)

        await browser.close()

        job_data = {
            "title": title,
            "description": page_text.strip(),
            "form_fields": extracted_fields,  # No need to clean empty fields
        }

        return job_data

def update_processing_table(url, job_data):
    """Update the database with scraped job data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE processing SET job_data=?, status='scraped' WHERE url=?", (json.dumps(job_data), url))
    conn.commit()
    conn.close()
    print(f"Updated processing table with scraped job: {url}")

async def process_next_job():
    """Move a job from queue to processing and scrape it."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, url FROM queue ORDER BY id ASC LIMIT 1")
    job = cursor.fetchone()

    if not job:
        print("No jobs in queue to scrape.")
        conn.close()
        return False

    job_id, job_url = job
    print(f"Processing job: {job_url}")

    # Move job to processing
    cursor.execute("DELETE FROM queue WHERE id=?", (job_id,))
    cursor.execute("INSERT INTO processing (url, status) VALUES (?, 'scraping')", (job_url,))
    conn.commit()
    conn.close()

    # Scrape job (now properly awaiting async function)
    job_data = await scrape_form(job_url)

    # --- HANDLE FAILURES EARLY ---
    move_to_unable_to_scrape = False
    failure_reason = ""

    # Case 1: Timeout or page load error
    if "error" in job_data:
        failure_reason = job_data["error"]
        move_to_unable_to_scrape = True

    # Case 2: Scrape returned "Unknown" title
    elif job_data.get("title") == "Unknown":
        failure_reason = "Unknown job title"
        move_to_unable_to_scrape = True

    # Case 3: Very short scraped content (< 1000 characters)
    else:
        total_length = (
            len(job_data.get("title", "").strip()) +
            len(job_data.get("description", "").strip()) +
            sum(len(f.get("label", "").strip()) for f in job_data.get("form_fields", []))
        )

        if total_length < 1000:
            failure_reason = f"Insufficient content ({total_length} chars)"
            move_to_unable_to_scrape = True

    # --- If any failure case was met, move to unable_to_scrape ---
    if move_to_unable_to_scrape:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Fetch the original job ID from processing before deleting
        cursor.execute("SELECT id FROM processing WHERE url=?", (job_url,))
        existing_id = cursor.fetchone()
        job_id = existing_id[0] if existing_id else None  # Keep original ID if exists

        # Convert scraped data to JSON format for storage
        full_job_data = json.dumps(job_data)

        # Insert into unable_to_scrape, keeping the original id if available
        if job_id:
            cursor.execute("""
                INSERT INTO unable_to_scrape (
                    id, url, error, added_at, job_title, job_data
                ) VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?, ?)
            """, (job_id, job_url, failure_reason, job_data.get("title", "Unknown"), full_job_data))
        else:
            cursor.execute("""
                INSERT INTO unable_to_scrape (
                    url, error, added_at, job_title, job_data
                ) VALUES (?, ?, CURRENT_TIMESTAMP, ?, ?)
            """, (job_url, failure_reason, job_data.get("title", "Unknown"), full_job_data))

        # REMOVE FROM PROCESSING IMMEDIATELY
        cursor.execute("DELETE FROM processing WHERE url=?", (job_url,))
        conn.commit()
        conn.close()

        print(f"BLOCKED: {job_url} -> {failure_reason}, moved to unable_to_scrape with full data, retaining id={job_id if job_id else 'NEW'}")
        return False  # STOP PROCESSING COMPLETELY

    # Otherwise, update processing with normal job data
    update_processing_table(job_url, job_data)
    return True

if __name__ == "__main__":
    process_next_job()
