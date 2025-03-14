import os
import re
import sqlite3
import openai
import json
import random
import PyPDF2
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
WRITER_MODEL = os.getenv("WRITER_MODEL", "gpt-4o")
FILE_NAME = os.getenv("FILE_NAME")
FULL_NAME = os.getenv("FULL_NAME")

# Paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
DB_DIR = os.path.join(ROOT_DIR, "db")
DB_PATH = os.path.join(DB_DIR, "data.db")
CONFIG_DIR = os.path.join(ROOT_DIR, "config")
USER_FILE = os.path.join(CONFIG_DIR, "user.json")
OUTPUT_DIR = os.path.join(ROOT_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_user_data():
    """Load user data from config/user.json."""
    if not os.path.exists(USER_FILE):
        print(f"User file not found at {USER_FILE}. Please create it.")
        return {}
    with open(USER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def process_next_writing_job():
    """Main job logic: get next scraping, decide JD, generate text, build PDFs."""
    user_data = load_user_data()
    if not user_data:
        print("No user data loaded. Cannot generate resumes/cover letters.")
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, url, job_data, JD, JD_reason, job_title
        FROM processing
        WHERE status='scraped'
        ORDER BY id ASC
        LIMIT 1
    """)
    row = cursor.fetchone()
    if not row:
        print("No jobs in 'scraped' status to write resumes/cover letters for.")
        conn.close()
        return False

    job_id, job_url, job_data_json, current_jd_value, jd_reason, job_title = row
    job_data = json.loads(job_data_json)
    conn.close()

    print(f"Preparing to generate resume & cover letter for job id={job_id}, url={job_url}")

    # 1) Decide JD approach if not set
    if not current_jd_value:
        approach, explanation, job_title = determine_jd_approach(job_data)
        conn = sqlite3.connect(DB_PATH)
        c2 = conn.cursor()
        c2.execute(
            "UPDATE processing SET JD=?, JD_reason=?, job_title=? WHERE id=?",
            (approach, explanation, job_title, job_id)
        )
        conn.commit()
        conn.close()
        current_jd_value = approach
        jd_reason = explanation
        print(f"Decided JD approach='{approach}' for job id={job_id}\nReason: {explanation}\nJob Title: {job_title}")
    else:
        print(f"JD approach already decided: {current_jd_value} for job id={job_id}")
        if jd_reason:
            print(f"Reason: {jd_reason}")
        if job_title:
            print(f"Job Title: {job_title}")

    # 2) Generate textual resume & cover letter
    resume_text, feedback = generate_resume_text(user_data, job_data, current_jd_value, jd_reason)
    cover_letter_text = generate_cover_letter_text(user_data, job_data, current_jd_value, jd_reason)

    # 3) Convert to PDF (reportlab)
    job_output_dir = os.path.join(OUTPUT_DIR, str(job_id))
    os.makedirs(job_output_dir, exist_ok=True)
    resume_pdf_path = os.path.join(job_output_dir, f"{FILE_NAME}_resume.pdf")
    cover_letter_pdf_path = os.path.join(job_output_dir, f"{FILE_NAME}_coverletter.pdf")

    # We'll store plain_text as the same (since GPT returns "reportlab" markup, 
    # but let's keep a fallback).
    plain_resume = strip_reportlab_tags(resume_text)
    plain_cover = strip_reportlab_tags(cover_letter_text)

    # Build PDFs
    create_pdf_reportlab(
        resume_text, resume_pdf_path, doc_title=f"{FULL_NAME}",
        leftMargin=0.5*inch, rightMargin=0.5*inch, topMargin=0.5*inch, bottomMargin=0.5*inch,
        job_title=job_title, creation_time_range=(2*24*60, 14*24*60)  # 2-14 days ago
    )

    create_pdf_reportlab(
        cover_letter_text, cover_letter_pdf_path, doc_title=f"{FULL_NAME} - Cover Letter for {job_title}",
        job_title=job_title, creation_time_range=(2, 60)  # 2-60 minutes ago
    )

    # Post-process PDFs to add metadata
    post_process_pdf(resume_pdf_path, f"{FULL_NAME}", job_title, creation_time_range=(2*24*60, 14*24*60))  # 2-14 days ago
    post_process_pdf(cover_letter_pdf_path, f"{FULL_NAME} - Cover Letter for {job_title}", job_title, creation_time_range=(2, 60))  # 2-60 minutes ago

    # 4) Update DB
    conn = sqlite3.connect(DB_PATH)
    c3 = conn.cursor()
    c3.execute("""
        UPDATE processing
        SET resume=?,
            resume_pdf=?,
            cover_letter=?,
            cover_letter_pdf=?,
            feedback=?,
            status='written'
        WHERE id=?
    """, (plain_resume, resume_pdf_path, plain_cover, cover_letter_pdf_path, feedback, job_id))
    conn.commit()
    conn.close()
    return True

def determine_jd_approach(job_data):
    """Ask GPT if we want JD-Advantage or JD-Light and get the job title."""
    prompt_text = f"""
You are an AI career counselor. The user might have a Juris Doctor (JD) background.
We have the following job data:
{json.dumps(job_data, indent=2)}

Decide if the user should highlight their JD (JD-Advantage) or downplay it (JD-Light).
On the first line, output exactly one of these strings: JD-Advantage or JD-Light
On the second line, give a short reason for your choice.
On the third line, provide the job title.
"""
    r = openai.chat.completions.create(
        model=WRITER_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful AI career counselor."},
            {"role": "user", "content": prompt_text}
        ],
        temperature=0.0,
        max_tokens=50
    )
    raw = r.choices[0].message.content.strip()
    lines = raw.split('\n')
    approach = "JD-Advantage"
    explanation = "No explanation provided."
    job_title = "Unknown"
    if lines:
        if "light" in lines[0].lower():
            approach = "JD-Light"
        elif "advantage" in lines[0].lower():
            approach = "JD-Advantage"
        if len(lines) > 1:
            explanation = lines[1].strip()
        if len(lines) > 2:
            job_title = lines[2].strip()
    return (approach, explanation, job_title)

def generate_resume_text(user_data, job_data, approach, jd_reason):
    special_instructions = user_data.get("special_instructions", [])
    instructions_str = "\n".join(f"- {ins}" for ins in special_instructions)
    job_json = json.dumps(job_data, indent=2)
    user_json = json.dumps(user_data, indent=2)

    advantage_line = ""
    if approach == "JD-Advantage" and jd_reason:
        advantage_line = f"\nAdditionally, highlight the JD advantage: {jd_reason}"

    extra_reportlab_line = """\nUse the following guidelines for formatting friendly with Python's ReportLab:
- For bold text, use <b>bold text</b>.
- For new lines, insert <br/>.
- For bullet points, start each bullet line with '• ' (no <bullet> tags).
- Wrap section headings in <h></h> for bigger font.
- Do not use XML beyond <b>, <br/>, <h> headings
- Return the entire resume as multiple lines of markup that ReportLab can parse.
"""

    prompt = f"""
You are a resume writer AI. The user is building a {approach} resume. Write a professional resume for the user.

Job Data:
{job_json}

User Data:
{user_json}

Special Instructions:
{instructions_str}{advantage_line}

Avoid false information.
Only incorporate what's valid from the user data.
Balance the resume with the JD approach in mind. JD-Advantage (push the JD) or JD-Light (minimize). 
Either way, highlight how the unique degree would benefit the job.
Balance the skills, experience, and education sections accordingly.
Do not include demographic information.
Do not include eligibility status other than willingness to relocate or travel.
Include phone number, email, website, and LinkedIn profile as a single line separated by | as the first line. Do not include a name.
Do not inclue any N/A, placeholders, hyperlinks, or brackets.
Write a paragraph for the summary section in an objective third person voice without using any first person pronouns or the user's name.
Explain how the user's experience and skills align with the job requirements and could benefit the company.
Include a skills section with a list of skills that are relevant to the job.
Inclue the dates next to the relevant experience.
Attept to minimize the resume to one page.
{extra_reportlab_line}
At the end return honest and objective feedback about the resume and user data. What could be done by the user to improve their odds of getting the job? What requirements did the user meet and not meet? What kind of data would have helped create a better resume? Is the user a good fit for the job? What are the chances the user gets interviewed for the position? Answer all questions and wrap all feedback in <f></f> tags.
"""
    resp = openai.chat.completions.create(
        model=WRITER_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful resume-writing assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_tokens=3000
    )
    response_text = resp.choices[0].message.content.strip()

    # Extract feedback wrapped in <f></f> tags
    feedback_match = re.search(r"<f>(.*?)</f>", response_text, re.DOTALL)
    feedback = feedback_match.group(1).strip() if feedback_match else ""

    # Remove feedback from the resume text
    resume_text = re.sub(r"<f>.*?</f>", "", response_text, flags=re.DOTALL).strip()

    return resume_text, feedback

def generate_cover_letter_text(user_data, job_data, approach, jd_reason):
    # (unchanged)
    today_str = datetime.today().strftime("%B %d, %Y")
    si = user_data.get("special_instructions", [])
    instructions_str = "\n".join(f"- {ins}" for ins in si)
    job_json = json.dumps(job_data, indent=2)
    user_json = json.dumps(user_data, indent=2)

    advantage_line = ""
    if approach == "JD-Advantage" and jd_reason:
        advantage_line = f"\nAdditionally, mention how the JD advantage helps: {jd_reason}"

    extra_reportlab_line = """\nUse the following guidelines for formatting:
- <b> for bold headings
- <br/> for new lines
- bullet lines starting with '• '
- <h> headings
No XML or <coverletter> tags - just text lines that ReportLab can parse.
"""

    prompt = f"""
You are a cover letter writer AI. The user has a base set of experiences and wants a professional {approach} cover letter.

Job Data:
{job_json}

User Data:
{user_json}

Special Instructions:
{instructions_str}{advantage_line}

Today's date: {today_str}.
- include date as first line formatted as Month DD, YYYY
- Under 1 page at 10 point font
- highlight the user's fit
- phone, email, LinkedIn under signature only.
- user's name as signature only, never at top
- mention job title & company in first paragraph
- mention willingness to relocate or travel
- mention how user chose position career over law
- do not use any N/A, placeholder text, hyperlinks, or brackets
- do not use formatting (such as **this**) other than <b>bold</b>, <br/>
- only include what's valid from user data
- avoid false information
- never include placeholders like [Employer Name] or Address placeholders, if you do not have the information, omit it
- only use paragraphs, do not include bullet points
"""
    r = openai.chat.completions.create(
        model=WRITER_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful cover letter-writing assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.9,
        max_tokens=2000
    )
    return r.choices[0].message.content.strip()

def strip_reportlab_tags(markup_text):
    """
    Convert lines with <b> or <br/> or '• ', <h> to plain text.
    Also remove any triple backticks.
    """
    markup_text = re.sub(r"```+", "", markup_text)

    lines = markup_text.splitlines()
    plain = []
    for ln in lines:
        # remove <b>...</b>
        no_b = re.sub(r"<b>(.*?)</b>", r"\1", ln)
        # remove <h>...</h>
        no_h = re.sub(r"<h>(.*?)</h>", r"\1", no_b)
        # remove <br/>
        no_br = no_h.replace("<br/>", "\n")
        # keep bullet lines but remove bullet symbol for plain text
        no_bullet = no_br.replace("• ", "- ")
        plain.append(no_bullet)
    return "\n".join(plain)

def create_pdf_reportlab(markup_text, pdf_path, doc_title="Document",
                         leftMargin=inch, rightMargin=inch,
                         topMargin=inch, bottomMargin=inch, job_title="", creation_time_range=(2*24*60, 14*24*60)):
    """
    - We have two doc types: resume vs cover letter. 
    - If doc_title has "Cover Letter", we do 10pt. Else 9pt for resume.
    - Headings (<h>...</h>) => bigger font (12).
    - Strip out triple backticks and parse line by line.
    - Center the first non-empty line after the doc title, i.e. contact info.
    """
    doc = SimpleDocTemplate(
        pdf_path, pagesize=LETTER, title=doc_title,
        leftMargin=leftMargin, rightMargin=rightMargin,
        topMargin=topMargin, bottomMargin=bottomMargin
    )
    styles = getSampleStyleSheet()
    # if it's a cover letter => 10pt, else => 9pt
    base_font_size = 11 if "Cover Letter" in doc_title else 8

    docTitleStyle = ParagraphStyle(
        'DocTitleStyle',
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=2,
        alignment=TA_CENTER
    )
    heading_style = ParagraphStyle(
        'HeadingStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=20,
        alignment=TA_LEFT
    )
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=base_font_size,
        leading=base_font_size+2,
        alignment=TA_LEFT
    )
    story = [
        Paragraph(doc_title, docTitleStyle),
        Spacer(1, 0.2*inch)
    ]

    first_line_found = False

    # Remove triple backticks **markdown** [brackets] and rogue formatting inclusions
    markup_text = re.sub(r"```+", "", markup_text)
    markup_text = re.sub(r"\*\*(.*?)\*\*", r"\1", markup_text)
    markup_text = re.sub(r"\[(.*?)\]", r"\1", markup_text)
    markup_text = re.sub(r"\b(plaintext|xml|markup|markdown)\b", "", markup_text, flags=re.IGNORECASE)

    # split lines
    lines = markup_text.split("\n")
    for ln in lines:
        line = ln.strip()
        if not line:
            story.append(Spacer(1, 0.1 * inch))
            continue

        # If line has <h> => heading
        if "<h>" in line:
            # parse out heading
            # e.g. <h>Some heading</h>
            heading_content = re.sub(r"<h>(.*?)</h>", r"\1", line)
            p = Paragraph(heading_content.upper(), heading_style)
            story.append(p)
            continue

        # bullet lines
        if line.startswith("• "):
            bullet_text = line[2:].strip()
            p = Paragraph(f"• {bullet_text}", body_style)
            story.append(p)
            continue

        # center the first non-empty line after doc title => contact info
        if not first_line_found:
            pstyle = ParagraphStyle(
                'CenterFirstLine',
                parent=body_style,
                alignment=TA_CENTER,
                fontSize=base_font_size,
                leading=base_font_size+2,
            )
            p = Paragraph(line, pstyle)
            story.append(p)
            first_line_found = True
            continue

        # handle <b>... 
        # or <br/> => we'll split
        chunks = line.split("<br/>")
        for c in chunks:
            c = c.strip()
            if not c:
                story.append(Spacer(1, 0.1*inch))
                continue
            final_text = c
            p2 = Paragraph(final_text, body_style)
            story.append(p2)

    # Build the PDF normally
    doc.build(story)

    # Post-process the PDF to add metadata
    post_process_pdf(pdf_path, doc_title, job_title, creation_time_range)

    print(f"{doc_title} PDF created: {pdf_path}")

def post_process_pdf(pdf_path, doc_title, job_title, creation_time_range):
    """Post-process the PDF to add metadata."""
    # Generate a random past date within the specified time range
    random_minutes_ago = random.randint(*creation_time_range)
    random_creation_date = datetime.now() - timedelta(minutes=random_minutes_ago)

    # Format creation date (D:YYYYMMDDHHMMSS)
    formatted_creation_date = f"(D:{random_creation_date.strftime('%Y%m%d%H%M%S')})"

    # Calculate ModDate as CreationDate plus 2-30 minutes, ensuring it doesn't exceed the present time
    random_minutes = random.randint(2, 30)
    mod_date = min(datetime.now(), random_creation_date + timedelta(minutes=random_minutes))
    formatted_mod_date = f"(D:{mod_date.strftime('%Y%m%d%H%M%S')})"

    # Read the just-built PDF
    with open(pdf_path, "rb") as original_pdf:
        reader = PyPDF2.PdfReader(original_pdf)
        writer = PyPDF2.PdfWriter()
        writer.append_pages_from_reader(reader)

        # Set or override metadata
        metadata = {
            "/Title": doc_title,
            "/Author": FULL_NAME,
            "/Subject": f"{FULL_NAME} Resume",
            "/Keywords": f"Resume, Cover Letter, {job_title}, {FULL_NAME}",
            "/Creator": "Microsoft Word",
            "/Producer": "Acrobat PDFMaker 21.0 for Word",
            "/CreationDate": formatted_creation_date,
            "/ModDate": formatted_mod_date
        }
        writer.add_metadata(metadata)

        # Write out the updated PDF (overwrite the original)
        with open(pdf_path, "wb") as updated_pdf:
            writer.write(updated_pdf)

    print(f"Metadata updated for {doc_title} PDF: {pdf_path}")