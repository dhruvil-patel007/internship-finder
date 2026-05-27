from flask import Flask, render_template, request
import sqlite3
import re

app = Flask(__name__)



def get_internships(location="", min_stipend=0, duration=""):
    conn   = sqlite3.connect("internships.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT title, company, location, stipend, duration, link
        FROM internships
    """)
    rows = cursor.fetchall()
    conn.close()

    results = []

    for row in rows:
        title, company, location_val, stipend, duration_val, link = row

       
        if location and location.lower() not in location_val.lower():
            continue

        
        if min_stipend > 0:
            numbers = re.findall(r"[\d,]+", stipend)
            amount  = int(numbers[0].replace(",", "")) if numbers else 0
            if amount < min_stipend:
                continue

        
        if duration and duration.lower() not in duration_val.lower():
            continue

        
        if link and not link.startswith("http"):
            link = "https://internshala.com" + link

        results.append({
            "title":    title,
            "company":  company,
            "location": location_val,
            "stipend":  stipend,
            "duration": duration_val,
            "link":     link,
        })

    return results



@app.route("/")
def index():
    location    = request.args.get("location", "").strip()
    min_stipend = int(request.args.get("min_stipend", 0) or 0)
    duration    = request.args.get("duration", "").strip()

    internships = get_internships(location, min_stipend, duration)

    return render_template(
        "index.html",
        internships = internships,
        location    = location,
        min_stipend = min_stipend,
        duration    = duration,
        total       = len(internships),
    )


if __name__ == "__main__":
    app.run(debug=True)
