import requests
from bs4 import BeautifulSoup

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
