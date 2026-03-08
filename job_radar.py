import requests
import smtplib
import os
import json
from email.mime.text import MIMEText

EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("PASSWORD")

HEADERS = {"User-Agent": "Mozilla/5.0"}

# --------------------------------------------------
# JOB TITLES YOU WANT TO TRACK
# --------------------------------------------------

KEYWORDS = [
"product owner",
"lead product owner",
"technical product owner",
"digital product manager",
"associate product manager",
"platform product manager",
"product manager",
"director of product",
"head of product",
"vp product"
]

# --------------------------------------------------
# CANADA LOCATION FILTER
# --------------------------------------------------

CANADA_LOCATIONS = [
"canada",
"toronto",
"montreal",
"vancouver",
"calgary",
"ottawa",
"remote canada"
]

# --------------------------------------------------
# ATS COMPANY LISTS
# --------------------------------------------------

GREENHOUSE_COMPANIES = [
"shopify",
"wealthsimple",
"clio",
"lightspeedhq",
"stackadapt"
]

LEVER_COMPANIES = [
"clearco",
"figment",
"koho",
"applyboard"
]

SMARTRECRUITERS_COMPANIES = [
"cognizant"
]

WORKABLE_COMPANIES = [
"pointclickcare"
]

# --------------------------------------------------
# SEEN JOB STORAGE
# --------------------------------------------------

def load_seen():

    try:
        with open("seen_jobs.json","r") as f:
            return set(json.load(f))
    except:
        return set()

def save_seen(seen):

    with open("seen_jobs.json","w") as f:
        json.dump(list(seen),f)

# --------------------------------------------------
# FILTER FUNCTION
# --------------------------------------------------

def is_target_job(title, location):

    title = title.lower()
    location = location.lower()

    if not any(k in title for k in KEYWORDS):
        return False

    if not any(loc in location for loc in CANADA_LOCATIONS):
        return False

    return True

# --------------------------------------------------
# GREENHOUSE
# --------------------------------------------------

def scan_greenhouse():

    jobs = []

    for company in GREENHOUSE_COMPANIES:

        url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"

        try:

            r = requests.get(url)
            data = r.json()

            for job in data["jobs"]:

                title = job["title"]
                location = job["location"]["name"]

                if is_target_job(title, location):

                    link = job["absolute_url"]

                    jobs.append(f"{company} — {title} ({location}) — {link}")

        except:
            pass

    return jobs

# --------------------------------------------------
# LEVER
# --------------------------------------------------

def scan_lever():

    jobs = []

    for company in LEVER_COMPANIES:

        url = f"https://api.lever.co/v0/postings/{company}?mode=json"

        try:

            r = requests.get(url)
            data = r.json()

            for job in data:

                title = job["text"]
                location = job["categories"]["location"]

                if is_target_job(title, location):

                    link = job["hostedUrl"]

                    jobs.append(f"{company} — {title} ({location}) — {link}")

        except:
            pass

    return jobs

# --------------------------------------------------
# WORKABLE
# --------------------------------------------------

def scan_workable():

    jobs = []

    for company in WORKABLE_COMPANIES:

        url = f"https://apply.workable.com/api/v3/accounts/{company}/jobs"

        try:

            r = requests.get(url)
            data = r.json()

            for job in data["results"]:

                title = job["title"]
                location = job["location"]["location_str"]

                if is_target_job(title, location):

                    link = job["shortcode"]

                    jobs.append(
                        f"{company} — {title} ({location}) — https://apply.workable.com/{company}/j/{link}"
                    )

        except:
            pass

    return jobs

# --------------------------------------------------
# SMARTRECRUITERS
# --------------------------------------------------

def scan_smartrecruiters():

    jobs = []

    for company in SMARTRECRUITERS_COMPANIES:

        url = f"https://api.smartrecruiters.com/v1/companies/{company}/postings"

        try:

            r = requests.get(url)
            data = r.json()

            for job in data["content"]:

                title = job["name"]
                location = job["location"]["city"]

                if is_target_job(title, location):

                    link = job["ref"]

                    jobs.append(
                        f"{company} — {title} ({location}) — https://careers.smartrecruiters.com/{company}/{link}"
                    )

        except:
            pass

    return jobs

# --------------------------------------------------
# EMAIL
# --------------------------------------------------

def send_email(job_list):

    if not job_list:
        return

    body = "\n\n".join(job_list)

    msg = MIMEText(body)
    msg["Subject"] = "New Product Jobs in Canada"
    msg["From"] = EMAIL
    msg["To"] = EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com",465) as smtp:

        smtp.login(EMAIL,PASSWORD)
        smtp.send_message(msg)

# --------------------------------------------------
# RUN RADAR
# --------------------------------------------------

seen = load_seen()

jobs = []
jobs += scan_greenhouse()
jobs += scan_lever()
jobs += scan_workable()
jobs += scan_smartrecruiters()

new_jobs = []

for job in jobs:

    if job not in seen:

        new_jobs.append(job)
        seen.add(job)

save_seen(seen)

send_email(new_jobs)


save_seen(seen)

send_email(new_jobs)

