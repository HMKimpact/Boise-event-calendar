import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template_string
import os

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
        date = date_tag.get_text(strip=True) if date_tag else "Unknown Date"
        time = time_tag.get_text(strip=True) if time_tag else ""
        location = location_tag.get_text(strip=True) if location_tag else "TBA"

        events.append({
            'title': title,
            'date': f"{date} {time}".strip(),
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
<head><title>Local Events Calendar</title></head>
<body>
    <h1>Local Events Calendar</h1>
    <ul>
    {% for event in events %}
        <li><strong>{{ event.date }}</strong> – {{ event.title }} at {{ event.location }} ({{ event.source }})</li>
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
