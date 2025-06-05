# app.py
# -*- coding: utf-8 -*-

import streamlit as st
import sqlite3
import re
from typing import List, Dict

# -------------------------
# Functions
# -------------------------

def search_mock_jobs(query: str, location: str = "") -> List[Dict]:
    sample_jobs = [
        {
            "title": f"{query} Developer",
            "company": "Tech Company A",
            "location": location or "Remote",
            "description": f"Looking for experienced {query} developer",
            "url": "https://example.com/job/1",
            "posted_date": "2025-06-01",
            "skills": [query.lower(), "python", "javascript"]
        },
        {
            "title": f"Senior {query}",
            "company": "Startup B",
            "location": location or "San Francisco, CA",
            "description": f"Senior {query} position with growth opportunities",
            "url": "https://example.com/job/2",
            "posted_date": "2025-06-02",
            "skills": [query.lower(), "react", "node.js"]
        }
    ]
    return sample_jobs

def simple_resume_parser(resume_text: str) -> Dict:
    skills_keywords = [
        'python', 'javascript', 'java', 'react', 'node.js', 'sql',
        'html', 'css', 'aws', 'docker', 'kubernetes', 'git',
        'machine learning', 'data science', 'ui/ux', 'design'
    ]

    text_lower = resume_text.lower()
    found_skills = [skill for skill in skills_keywords if skill in text_lower]

    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'

    emails = re.findall(email_pattern, resume_text)
    phones = re.findall(phone_pattern, resume_text)

    return {
        "skills": found_skills,
        "email": emails[0] if emails else "Not found",
        "phone": phones[0] if phones else "Not found",
        "text_length": len(resume_text),
        "word_count": len(resume_text.split())
    }

def init_db():
    conn = sqlite3.connect('job_search.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS saved_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    company TEXT,
                    location TEXT,
                    description TEXT,
                    url TEXT,
                    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def save_job(job_data: Dict):
    conn = sqlite3.connect('job_search.db')
    c = conn.cursor()
    c.execute("""INSERT INTO saved_jobs (title, company, location, description, url)
                 VALUES (?, ?, ?, ?, ?)""",
              (job_data.get('title', ''), job_data.get('company', ''),
               job_data.get('location', ''), job_data.get('description', ''),
               job_data.get('url', '')))
    conn.commit()
    conn.close()

def get_saved_jobs():
    conn = sqlite3.connect('job_search.db')
    c = conn.cursor()
    c.execute("SELECT * FROM saved_jobs ORDER BY saved_at DESC")
    jobs = c.fetchall()
    conn.close()
    return jobs

# -------------------------
# Initialize DB
# -------------------------
init_db()

# -------------------------
# Streamlit UI
# -------------------------

st.title("Job Search AI & Resume Analyzer")

st.header("🔍 Search Jobs")
query = st.text_input("Enter job role (e.g., Python Developer):")
location = st.text_input("Enter location (or leave blank for Remote):")

if st.button("Search Jobs"):
    if query.strip() == "":
        st.warning("Please enter a job role to search.")
    else:
        results = search_mock_jobs(query, location)
        st.success(f"Found {len(results)} job(s):")
        for i, job in enumerate(results):
            st.subheader(f"{i+1}. {job['title']} at {job['company']} - {job['location']}")
            st.write(f"**Description:** {job['description']}")
            st.write(f"**URL:** [Link]({job['url']})")
            st.write(f"**Skills:** {', '.join(job['skills'])}")

            if st.button(f"Save Job #{i+1}"):
                save_job(job)
                st.success("✅ Job saved!")

st.header("📄 Resume Analysis")
resume_text = st.text_area("Paste your resume text here:")

if st.button("Analyze Resume"):
    if not resume_text.strip():
        st.warning("Please paste your resume text first.")
    else:
        parsed = simple_resume_parser(resume_text)
        st.write(f"**Email:** {parsed['email']}")
        st.write(f"**Phone:** {parsed['phone']}")
        st.write(f"**Word Count:** {parsed['word_count']}")
        st.write(f"**Character Count:** {parsed['text_length']}")
        st.write(f"**Skills Found:** {', '.join(parsed['skills']) if parsed['skills'] else 'None'}")

st.header("💾 Saved Jobs")
saved_jobs = get_saved_jobs()
if saved_jobs:
    for job in saved_jobs:
        st.write(f"- **{job[1]}** at {job[2]} ({job[3]}) - saved on {job[6]}")
else:
    st.info("No saved jobs yet.")

