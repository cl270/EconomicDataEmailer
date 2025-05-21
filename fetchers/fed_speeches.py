import feedparser
import requests
from datetime import datetime

FEED_URL = 'https://www.federalreserve.gov/feeds/speeches.xml'

def fetch_fed_speeches() -> dict:
    d = feedparser.parse(FEED_URL)
    if not d.entries:
        return {"timestamp": datetime.utcnow().isoformat(), "error": "No entries"}
    latest = d.entries[0]
    link = latest.link
    resp = requests.get(link, timeout=10)
    text = resp.text
    return {
        "title": latest.title,
        "link": link,
        "text": text,
        "timestamp": datetime.utcnow().isoformat()
    }
