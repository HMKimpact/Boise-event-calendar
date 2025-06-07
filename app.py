from flask import Flask, render_template_string
import os

# You probably already have your `scrape_bndry()` and `get_all_events()` above this

app = Flask(__name__)

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
    print(events)  # For logging to Render
    return render_template_string(template, events=events)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
