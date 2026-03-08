import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText

EMAIL = "your_email@gmail.com"
PASSWORD = "your_app_password"

KEYWORDS = [
"product owner",
"product manager",
"digital product manager",
"technical product manager",
"agile product owner"
]

HEADERS = {"User-Agent": "Mozilla/5.0"}

# -----------------------------
# JOB BOARDS
# -----------------------------

JOB_BOARD_URLS = [

"https://www.indeed.com/jobs?q=product+owner&l=Canada",
"https://www.indeed.com/jobs?q=product+manager&l=Canada",

"https://www.linkedin.com/jobs/search/?keywords=product%20owner&location=Canada",
"https://www.linkedin.com/jobs/search/?keywords=product%20manager&location=Canada"

]

# -----------------------------
# COMPANY CAREER PAGES
# -----------------------------

COMPANY_CAREERS = [

# Banks & Financial
"https://jobs.rbc.com",
"https://jobs.td.com",
"https://jobs.scotiabank.com",
"https://jobs.bmo.com",
"https://careers.cibc.com",
"https://www.eqbank.ca/careers",
"https://careers.questrade.com",
"https://careers.wealthsimple.com",

# Insurance
"https://careers.manulife.com",
"https://sunlife.wd3.myworkdayjobs.com",
"https://careers.intactfc.com",
"https://careers.greatwestlife.com",

# Telecom
"https://jobs.rogers.com",
"https://jobs.bell.ca",
"https://careers.telus.com",

# Canadian Tech
"https://www.shopify.com/careers",
"https://www.lightspeedhq.com/careers",
"https://careers.opentext.com",
"https://jobs.lever.co/clio",

# SaaS
"https://jobs.lever.co/clearco",
"https://jobs.lever.co/stackadapt",
"https://jobs.lever.co/wealthsimple",

# Consulting
"https://careers.accenture.com",
"https://www2.deloitte.com/careers",
"https://home.kpmg/ca/en/home/careers.html",
"https://www.capgemini.com/careers",
"https://careers.cognizant.com",

# Retail / Ecommerce
"https://careers.loblaw.ca",
"https://corp.canadiantire.ca/careers",
"https://www.chapters.indigo.ca/en-ca/careers",

# Startups
"https://jobs.lever.co/figment",
"https://jobs.lever.co/koho",
"https://jobs.lever.co/wealthsimple",

]

# -----------------------------
# JOB SCRAPER
# -----------------------------

def scan_pages(urls):

    jobs = []

    for url in urls:

        try:

            r = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")

            for a in soup.find_all("a"):

                title = a.text.strip()

                if any(k in title.lower() for k in KEYWORDS):

                    link = a.get("href")

                    if link:

                        if link.startswith("/"):
                            link = url + link

                        jobs.append(f"{title} — {link}")

        except:
            pass

    return jobs

# -----------------------------
# EMAIL SENDER
# -----------------------------

def send_email(job_list):

    if not job_list:
        return

    body = "\n\n".join(job_list)

    msg = MIMEText(body)
    msg["Subject"] = "New Product Owner / PM Jobs"
    msg["From"] = EMAIL
    msg["To"] = EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:

        smtp.login(EMAIL, PASSWORD)
        smtp.send_message(msg)

# -----------------------------
# RUN SCANNER
# -----------------------------

jobs1 = scan_pages(JOB_BOARD_URLS)
jobs2 = scan_pages(COMPANY_CAREERS)

all_jobs = list(set(jobs1 + jobs2))

send_email(all_jobs)
