from flask import Flask, render_template_string
from bs4 import BeautifulSoup

app = Flask(__name__)

def scrape_bndry():
    html = """
    <div class="event-container">
        <h2>Drag Bingo Night</h2>
        <time datetime="2025-06-15T19:00">June 15, 7:00 PM</time>
        <div class="location">BNDRY Club, Boise</div>
    </div>
    """
    soup = BeautifulSoup(html, 'html.parser')
    events = []
    for event in soup.find_all('div', class_='event-container'):
        events.append({
            'title': event.find('h2').text.strip(),
            'date': event.find('time')['datetime'],
            'location': event.find('div', class_='location').text.strip(),
            'source': 'BNDRY'
        })
    return events

def scrape_eventbrite():
    html = """
    <div class="card">
        <div class="title">Green Business Meetup</div>
        <div class="date">2025-06-20</div>
        <div class="place">JUMP Boise</div>
    </div>
    """
    soup = BeautifulSoup(html, 'html.parser')
    events = []
    for event in soup.find_all('div', class_='card'):
        events.append({
            'title': event.find('div', class_='title').text.strip(),
            'date': event.find('div', class_='date').text.strip(),
            'location': event.find('div', class_='place').text.strip(),
            'source': 'Eventbrite'
        })
    return events

def get_all_events():
    return scrape_bndry() + scrape_eventbrite()

template = """
<!DOCTYPE html>
<html>
<head><title>Local Events</title></head>
<body>
    <h1>Local Events Calendar</h1>
    <ul>
    {% for event in events %}
        <li><strong>{{ event.title }}</strong> - {{ event.date }} at {{ event.location }} ({{ event.source }})</li>
    {% endfor %}
    </ul>
</body>
</html>
"""

@app.route('/')
def calendar():
    events = get_all_events()
    return render_template_string(template, events=events)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)