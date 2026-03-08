import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os
import json

EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("PASSWORD")

HEADERS = {"User-Agent": "Mozilla/5.0"}

KEYWORDS = [
"product owner",
"product manager",
"digital product manager",
"technical product manager",
"agile product owner"
]

# --------------------------------
# TARGET COMPANY CAREER PAGES
# --------------------------------

COMPANY_CAREERS = [

# Banks & Financial Services
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

# Telecom & Media
"https://jobs.rogers.com",
"https://jobs.bell.ca",
"https://careers.telus.com",

# Canadian Tech / SaaS
"https://www.shopify.com/careers",
"https://www.lightspeedhq.com/careers",
"https://careers.opentext.com",
"https://jobs.lever.co/clio",

# Consulting / IT Services
"https://careers.accenture.com",
"https://www2.deloitte.com/careers",
"https://home.kpmg/ca/en/home/careers.html",
"https://www.capgemini.com/careers",
"https://careers.cognizant.com",

# Retail / Ecommerce
"https://careers.loblaw.ca",
"https://corp.canadiantire.ca/careers",
"https://www.chapters.indigo.ca/en-ca/careers"

]

# --------------------------------
# LOAD SEEN JOBS
# --------------------------------

def load_seen():

    try:
        with open("seen_jobs.json","r") as f:
            return set(json.load(f))
    except:
        return set()

def save_seen(seen):

    with open("seen_jobs.json","w") as f:
        json.dump(list(seen),f)

# --------------------------------
# SCAN COMPANY PAGES
# --------------------------------

def scan_pages():

    jobs = []

    for url in COMPANY_CAREERS:

        try:

            r = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(r.text,"html.parser")

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

# --------------------------------
# SEND EMAIL
# --------------------------------

def send_email(job_list):

    if not job_list:
        return

    body = "\n\n".join(job_list)

    msg = MIMEText(body)
    msg["Subject"] = "New Product Owner / PM Jobs Found"
    msg["From"] = EMAIL
    msg["To"] = EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com",465) as smtp:

        smtp.login(EMAIL,PASSWORD)
        smtp.send_message(msg)

# --------------------------------
# MAIN
# --------------------------------

seen_jobs = load_seen()

found_jobs = scan_pages()

new_jobs = []

for job in found_jobs:

    if job not in seen_jobs:

        new_jobs.append(job)
        seen_jobs.add(job)

save_seen(seen_jobs)

send_email(new_jobs)

