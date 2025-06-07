import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template_string
import os
from datetime import datetime

app = Flask(__name__)

# ---- FLEXIBLE DATE PARSER ----
def parse_date_flexibly(date_str):
    for fmt in ['%B %d, %Y', '%A, %B %d, %Y', '%A, %B %d']:
        try:
            parsed = datetime.strptime(date_str, fmt)
            if '%Y' not in fmt:
                parsed = parsed.replace(year=datetime.today().year)
            return parsed
        except ValueError:
            continue
    return None

# ---- SCRAPE BNDRY ----
def scrape_bndry():
    url = "https://www.bndry.club/club-calendar"
    headers = {'User-Agent': 'Mozilla/5.0'}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    events = []
    today = datetime.today()

    for event in soup.select('article.eventlist-event'):
        title_tag = event.select_one('h1.eventlist-title')
        date_tag = event.select_one('li.eventlist-meta-date')
        time_tag = event.select_one('li.eventlist-meta-time')
        location_tag = event.select_one('li.eventlist-meta-address')

        title = title_tag.get_text(strip=True) if title_tag else "Untitled"
        date_str = date_tag.get_text(strip=True) if date_tag else "Unknown Date"
        time_str = time_tag.get_text(strip=True) if time_tag else "Unknown Time"
        location = location_tag.get_text(strip=True) if location_tag else "TBA"

        print("RAW DATE:", date_str)

        event_date = parse_date_flexibly(date_str)
        if not event_date:
            continue

        if event_date >= today:
            events.append({
                'title': title,
                'date': date_str,
                'time': time_str,
                'location': location,
                'source': 'BNDRY'
            })

    return events

# ---- AGGREGATOR ----
def get_all_events():
    return scrape_bndry()

# ---- HTML TEMPLATE ----
template = """
<!DOCTYPE html>
<html>
<head>
  <title>Boise Events Calendar</title>
  <style>
    body {
      font-family: Arial, sans-serif;
    }
  </style>
</head>
<body>
    <h1>Boise Events Calendar</h1>
    <ul>
    {% for event in events %}
        <li>{{ event.date }}, {{ event.time }} — <strong>{{ event.title }}</strong>, {{ event.location }} ({{ event.source }})</li>
    {% else %}
        <li>No events found.</li>
    {% endfor %}
    </ul>
</body>
</html>
"""

# ---- FLASK ROUTE ----
@app.route('/')
def calendar():
    events = get_all_events()
    print(events)
    return render_template_string(template, events=events)

# ---- RUN SERVER ON CORRECT PORT ----
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

