import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template_string, jsonify
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
    today = datetime.today()

    for event in soup.select('article.eventlist-event'):
        title_tag = event.select_one('h1.eventlist-title')
        time_tag = event.select_one('li.eventlist-meta-time')
        location_tag = event.select_one('li.eventlist-meta-address')
        datetime_tag = event.select_one('time')

        title = title_tag.get_text(strip=True) if title_tag else "Untitled"
        time_str = time_tag.get_text(strip=True) if time_tag else "Unknown Time"
        location = location_tag.get_text(strip=True) if location_tag else "TBA"
        raw_datetime = datetime_tag.get('datetime') if datetime_tag else None

        try:
            event_date = datetime.strptime(raw_datetime, '%Y-%m-%d')
        except:
            continue

        if event_date >= today:
            events.append({
                'title': title,
                'date': event_date.strftime('%B %d, %Y'),
                'time': time_str,
                'location': location,
                'source': 'BNDRY'
            })

    return events

# ---- AGGREGATOR ----
def get_all_events():
    return scrape_bndry()

# ---- HTML TEMPLATE (FullCalendar) ----
template = """
<!DOCTYPE html>
<html>
<head>
  <title>Boise Events Calendar</title>
  <link href='https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/main.min.css' rel='stylesheet' />
  <script src='https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/main.min.js'></script>
  <style>
    body {
      font-family: Arial, sans-serif;
      margin: 40px;
    }
    #calendar {
      max-width: 900px;
      margin: 0 auto;
    }
  </style>
</head>
<body>
  <h1>Boise Events Calendar</h1>
  <div id='calendar'></div>

  <script>
    document.addEventListener('DOMContentLoaded', function () {
      var calendarEl = document.getElementById('calendar');

      var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        events: '/events.json',
        eventDidMount: function (info) {
          info.el.title = info.event.extendedProps.display_date + ' at ' +
                          info.event.extendedProps.time + '\\n' +
                          info.event.extendedProps.location + ' (' +
                          info.event.extendedProps.source + ')';
        }
      });

      calendar.render();
    });
  </script>
</body>
</html>
"""

# ---- MAIN ROUTE ----
@app.route('/')
def calendar():
    events = get_all_events()
    return render_template_string(template, events=events)

# ---- JSON ROUTE FOR CALENDAR ----
@app.route('/events.json')
def events_json():
    events = get_all_events()
    calendar_events = []

    for event in events:
        try:
            date_obj = datetime.strptime(event['date'], '%B %d, %Y')
            iso_date = date_obj.strftime('%Y-%m-%d')
        except Exception:
            continue

        calendar_events.append({
            "title": event['title'],
            "start": iso_date,
            "extendedProps": {
                "display_date": event['date'],
                "time": event['time'],
                "location": event['location'],
                "source": event['source']
            }
        })

    return jsonify(calendar_events)

# ---- START SERVER ----
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
