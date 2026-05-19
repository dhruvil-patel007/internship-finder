

from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# ── Database se data laane ka helper ──────────
def get_internships(location="", min_stipend=0):
    conn   = sqlite3.connect("internships.db")
    cursor = conn.cursor()

    # Sab internships laao
    cursor.execute("SELECT title, company, location, stipend, duration FROM internships")
    rows = cursor.fetchall()
    conn.close()
 
    results = []
    for row in rows:
        title, company, location_val, stipend, duration = row

        # Location filter
        if location and location.lower() not in location_val.lower():
            continue

        # Stipend filter
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


# ── Main page ─────────────────────────────────
@app.route("/")
def index():
    # URL se filter values lo — user ne kya search kiya
    location    = request.args.get("location", "")
    min_stipend = int(request.args.get("min_stipend", 0) or 0)

    internships = get_internships(location, min_stipend)
    
    
    return render_template("index.html",
        internships  = internships,
        location     = location,
        min_stipend  = min_stipend,
        total        = len(internships)
    )


# ── App chalao ────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)