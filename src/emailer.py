import os
import sqlite3
import smtplib
import ssl
from email.message import EmailMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db", "data.db")

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

EMAIL_FROM = os.getenv("EMAIL_FROM")  # e.g. "noreply@yourdomain.com"
EMAIL_TO = os.getenv("EMAIL_TO")      # your personal address

def check_and_send_emails():
    """Check the processed table for any row where emailed=0, then send the email with attachments."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Grab all rows in 'processed' that haven't been emailed yet
    cursor.execute("""
        SELECT id, job_title, job_company, JD, JD_reason, started_at, finished_at,
               feedback, resume_pdf, cover_letter_pdf
        FROM processed
        WHERE emailed=0
    """)
    rows = cursor.fetchall()

    if not rows:
        print("No new processed entries to email.")
        conn.close()
        return

    # For each row, send an email, then update
    for row in rows:
        (job_id, job_title, job_company, JD, JD_reason, started_at,
         finished_at, feedback, resume_pdf, cover_letter_pdf) = row

        # Build and send the email
        send_email_with_attachments(
            job_id, job_title, job_company,
            JD, JD_reason, started_at, finished_at,
            feedback, resume_pdf, cover_letter_pdf
        )

        # Update the DB to mark emailed=1 (true)
        cursor.execute("UPDATE processed SET emailed=1 WHERE id=?", (job_id,))
        conn.commit()

    conn.close()


def send_email_with_attachments(job_id, job_title, job_company,
                                JD, JD_reason, started_at, finished_at,
                                feedback, resume_pdf, cover_letter_pdf):
    """Construct and send the email via SMTP."""

    subject = f"cronjob: {job_id} - {job_title} - {job_company}"
    body = (
        f"cronjob #{job_id}\n"
        f"{job_title} at {job_company}\n"
        f"{JD}: {JD_reason}\n"
        f"Started: {started_at}\n"
        f"Finished: {finished_at}\n\n"
        f"{feedback}\n"
    )

    msg = EmailMessage()
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject
    msg.set_content(body)

    # Attach the PDFs (resume & cover letter)
    # Make sure the files actually exist
    for pdf_path in [resume_pdf, cover_letter_pdf]:
        if pdf_path and os.path.isfile(pdf_path):
            with open(pdf_path, "rb") as f:
                file_data = f.read()
            filename = os.path.basename(pdf_path)
            # The maintype is "application", the subtype is "pdf"
            msg.add_attachment(file_data, maintype="application", subtype="pdf", filename=filename)

    # Connect and send
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)


    print(f"Email sent successfully for job_id={job_id} to {EMAIL_TO}.\n")


if __name__ == "__main__":
    # You can either run this module manually, or set up a schedule (cron) to run it periodically
    check_and_send_emails()