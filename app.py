from flask import Flask, render_template_string
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def scrape_bndry():
    url = "https://www.bndry.club/club-calendar"
    headers = {'User-Agent': 'Mozilla/5.0'}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    events = []

    # Adjust selectors based on actual page structure
    for card in soup.select('.event-card, .event-item, .calendar-event'):
        title = card.select_one('.event-title, h3, h2')
        date = card.select_one('time')
        location = card.select_one('.event-location, .location, .venue')

        if title and date:
            events.append({
                'title': title.get_text(strip=True),
                'date': date.get('datetime') or date.get_text(strip=True),
                'location': location.get_text(strip=True) if location else 'TBA',
                'source': 'BNDRY'
            })
    return events

def get_all_events():
    return scrape_bndry()

template = """
<!DOCTYPE html>
<html>
<head><title>Local Events</title></head>
<body>
  <h1>Local Events Calendar</h1>
  <ul>
    {% for e in events %}
      <li><strong>{{ e.title }}</strong> – {{ e.date }} at {{ e.location }}</li>
    {% else %}
      <li>No events found.</li>
    {% endfor %}
  </ul>
</body>
</html>
"""

@app.route('/')
def calendar():
    events = get_all_events()
    print(events)  # For logs debugging
    return render_template_string(template, events=events)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
