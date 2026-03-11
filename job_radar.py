import requests
import smtplib
import os
import json
from email.mime.text import MIMEText

EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("PASSWORD")
HEADERS = {"User-Agent": "Mozilla/5.0"}

# -----------------------------
# JOB TITLES TO TRACK
# -----------------------------
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

# -----------------------------
# CANADA LOCATIONS
# -----------------------------
CANADA_LOCATIONS = [
    "canada",
    "toronto",
    "montreal",
    "vancouver",
    "calgary",
    "ottawa",
    "remote canada"
]

# -----------------------------
# ATS COMPANY LISTS
# -----------------------------
GREENHOUSE_COMPANIES = ["shopify","wealthsimple","clio","lightspeedhq","stackadapt"]
LEVER_COMPANIES = ["clearco","figment","koho","applyboard"]
SMARTRECRUITERS_COMPANIES = ["cognizant"]
WORKABLE_COMPANIES = ["pointclickcare"]

# -----------------------------
# WORKDAY API COMPANIES
# -----------------------------
WORKDAY_API_COMPANIES = {
    "rbc":"https://jobs.rbc.com/wday/cxs/rbc/jobs/jobs",
    "td":"https://jobs.td.com/wday/cxs/td/jobs/jobs",
    "scotiabank":"https://jobs.scotiabank.com/wday/cxs/scotiabank/jobs/jobs",
    "telus":"https://careers.telus.com/wday/cxs/telus/jobs/jobs",
    "accenture":"https://careers.accenture.com/wday/cxs/accenture/jobs/jobs",
    "cibc":"https://careers.cibc.com/wday/cxs/cibc/jobs/jobs",
    "sunlife":"https://sunlife.wd3.myworkdayjobs.com/wday/cxs/sunlife/jobs/jobs",
    "manulife":"https://manulife.wd3.myworkdayjobs.com/wday/cxs/manulife/jobs/jobs"
}

# -----------------------------
# SEEN JOB STORAGE
# -----------------------------
SEEN_FILE = "seen_jobs.json"

def load_seen():
    try:
        with open(SEEN_FILE,"r") as f:
            return set(json.load(f))
    except:
        return set()

def save_seen(seen):
    with open(SEEN_FILE,"w") as f:
        json.dump(list(seen),f)

# -----------------------------
# FILTER FUNCTION
# -----------------------------
def is_target_job(title, location):
    title = title.lower()
    location = location.lower()
    if not any(k in title for k in KEYWORDS):
        return False
    if not any(loc in location for loc in CANADA_LOCATIONS):
        return False
    return True

# -----------------------------
# SCANNERS
# -----------------------------
def scan_greenhouse():
    jobs=[]
    for company in GREENHOUSE_COMPANIES:
        try:
            r=requests.get(f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs",headers=HEADERS,timeout=10)
            data=r.json()
            for job in data.get("jobs",[]):
                title=job["title"]
                location=job["location"]["name"]
                if is_target_job(title,location):
                    jobs.append(f"{company} — {title} ({location}) — {job['absolute_url']}")
        except:
            pass
    return jobs

def scan_lever():
    jobs=[]
    for company in LEVER_COMPANIES:
        try:
            r=requests.get(f"https://api.lever.co/v0/postings/{company}?mode=json",headers=HEADERS,timeout=10)
            data=r.json()
            for job in data:
                title=job["text"]
                location=job["categories"]["location"]
                if is_target_job(title,location):
                    jobs.append(f"{company} — {title} ({location}) — {job['hostedUrl']}")
        except:
            pass
    return jobs

def scan_workable():
    jobs=[]
    for company in WORKABLE_COMPANIES:
        try:
            r=requests.get(f"https://apply.workable.com/api/v3/accounts/{company}/jobs",headers=HEADERS,timeout=10)
            data=r.json()
            for job in data.get("results",[]):
                title=job["title"]
                location=job["location"]["location_str"]
                if is_target_job(title,location):
                    link=job["shortcode"]
                    jobs.append(f"{company} — {title} ({location}) — https://apply.workable.com/{company}/j/{link}")
        except:
            pass
    return jobs

def scan_smartrecruiters():
    jobs=[]
    for company in SMARTRECRUITERS_COMPANIES:
        try:
            r=requests.get(f"https://api.smartrecruiters.com/v1/companies/{company}/postings",headers=HEADERS,timeout=10)
            data=r.json()
            for job in data.get("content",[]):
                title=job["name"]
                location=job["location"]["city"]
                if is_target_job(title,location):
                    link=job["ref"]
                    jobs.append(f"{company} — {title} ({location}) — https://careers.smartrecruiters.com/{company}/{link}")
        except:
            pass
    return jobs

def scan_workday_api():
    jobs=[]
    payload={"limit":50,"offset":0,"searchText":""}
    for company,url in WORKDAY_API_COMPANIES.items():
        try:
            r=requests.post(url,json=payload,headers=HEADERS,timeout=10)
            data=r.json()
            for job in data.get("jobPostings",[]):
                title=job["title"]
                location=job.get("locationsText","")
                if is_target_job(title,location):
                    link="https://"+url.split("/")[2]+job["externalPath"]
                    jobs.append(f"{company} — {title} ({location}) — {link}")
        except:
            pass
    return jobs

# -----------------------------
# SEND EMAIL
# -----------------------------
#def send_email(job_list):
 #   if not job_list:
  #      return
   # body="\n\n".join(job_list)
    #msg=MIMEText(body)
  #  msg["Subject"]="New Product Jobs in Canada"
  #  msg["From"]=EMAIL
  #  msg["To"]=EMAIL
  #  with smtplib.SMTP_SSL("smtp.gmail.com",465) as smtp:
  #      smtp.login(EMAIL,PASSWORD)
   #     smtp.send_message(msg)

# -----------------------------
# RUN RADAR
# -----------------------------
seen = load_seen()

jobs=[]
jobs += scan_greenhouse()
jobs += scan_lever()
jobs += scan_workable()
jobs += scan_smartrecruiters()
jobs += scan_workday_api()

new_jobs=[]
for job in jobs:
    if job not in seen:
        new_jobs.append(job)
        seen.add(job)

save_seen(seen)
send_email(new_jobs)
