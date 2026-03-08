import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText

KEYWORDS = ["Product Owner", "Product Manager"]
LOCATIONS = ["Canada", "Remote"]

URLS = [
    "https://www.indeed.com/jobs?q=product+owner&l=Canada",
    "https://www.indeed.com/jobs?q=product+manager&l=Canada"
]

def get_jobs():
    jobs = []
    for url in URLS:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")

        for job in soup.select("a"):
            title = job.text.strip()

            if any(k.lower() in title.lower() for k in KEYWORDS):
                link = "https://www.indeed.com" + job.get("href", "")
                jobs.append(f"{title} — {link}")

    return list(set(jobs))


def send_email(jobs):
    if not jobs:
        return

    msg = MIMEText("\n\n".join(jobs))
    msg["Subject"] = "New Product Owner Jobs"
    msg["From"] = EMAIL
    msg["To"] = EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL, PASSWORD)
        smtp.send_message(msg)


EMAIL = "your_email@gmail.com"
PASSWORD = "your_app_password"

jobs = get_jobs()
send_email(jobs)

