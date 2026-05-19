from flask import Flask, render_template, request
import sqlite3
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("internships.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS internships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, company TEXT,
            location TEXT, stipend TEXT, duration TEXT
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM internships")
    count = cursor.fetchone()[0]

    if count == 0:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get("https://internshala.com/internships/", headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        jobs = soup.find_all("div", class_="individual_internship")

        for job in jobs:
            title_tag    = job.find("a", class_="job-title-href")
            company_tag  = job.find("p", class_="company-name")
            location_tag = job.find("div", class_="row-1-item locations")
            stipend_tag  = job.find("span", class_="stipend")
            duration_tag = job.find("i", class_="ic-16-calendar")

            def get_text(tag):
                return tag.get_text(separator=" ").strip() if tag else "Not specified"

            title    = get_text(title_tag)
            company  = get_text(company_tag)
            location = get_text(location_tag)
            stipend  = get_text(stipend_tag)
            duration = get_text(duration_tag.find_next("span")) if duration_tag else "Not specified"

            if title_tag:
                cursor.execute("""
                    INSERT INTO internships (title, company, location, stipend, duration)
                    VALUES (?, ?, ?, ?, ?)
                """, (title, company, location, stipend, duration))

        conn.commit()
    conn.close()

init_db()

def get_internships(location="", min_stipend=0):
    conn   = sqlite3.connect("internships.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title, company, location, stipend, duration FROM internships")
    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        title, company, location_val, stipend, duration = row

        if location and location.lower() not in location_val.lower():
            continue

        if min_stipend > 0:
            import re
            numbers = re.findall(r"[\d,]+", stipend)
            amount  = int(numbers[0].replace(",", "")) if numbers else 0
            if amount < min_stipend:
                continue

        results.append({
            "title":    title,
            "company":  company,
            "location": location_val,
            "stipend":  stipend,
            "duration": duration,
        })

    return results


@app.route("/")
def index():
    location    = request.args.get("location", "")
    min_stipend = int(request.args.get("min_stipend", 0) or 0)

    internships = get_internships(location, min_stipend)

    return render_template("index.html",
        internships = internships,
        location    = location,
        min_stipend = min_stipend,
        total       = len(internships)
    )


if __name__ == "__main__":
    app.run(debug=True)
