import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template_string
import os
from datetime import datetime

app = Flask(__name__)

# ---- SCRAPE BNDRY ----
def scrape_bndry():
    url = "https://www.bndry.club/club-calendar"
    headers = {'User-Agent': 'Mozilla/5.0'}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    events = []

    for event in soup.select('article.eventlist-event'):
        title_tag = event.select_one('h1.eventlist-title')
        date_tag = event.select_one('li.eventlist-meta-date')
        time_tag = event.select_one('li.eventlist-meta-time')
        location_tag = event.select_one('li.eventlist-meta-address')

        title = title_tag.get_text(strip=True) if title_tag else "Untitled"
        date_str = date_tag.get_text(strip=True) if date_tag else "Unknown Date"
        time_str = time_tag.get_text(strip=True) if time_tag else "Unknown Time"
        location = location_tag.get_text(strip=True) if location_tag else "TBA"

        # Try to parse the date into a sortable format
        try:
            date_obj = datetime.strptime(date_str, '%B %d, %Y')
        except Exception:
            date_obj = datetime.max  # Push to bottom if unreadable

        events.append({
            'title': title,
            'date': date_str,
            'time': time_str,
            'location': location,
            'source': 'BNDRY',
            'sort_date': date_obj
        })

    # Sort by date (soonest first)
    events.sort(key=lambda x: x['sort_date'])
    return events

# ---- AGGREGATOR ----
def get_all_events():
    return scrape_bndry()

# ---- HTML TEMPLATE ----
template = """
<!DOCTYPE html>
<html>
<head><title>Local Events Calendar</title></head>
<body>
    <h1>Local Events Calendar</h1>
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
    print(events)  # for Render logs
    return render_template_string(template, events=events)

# ---- RUN SERVER ON CORRECT PORT ----
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
