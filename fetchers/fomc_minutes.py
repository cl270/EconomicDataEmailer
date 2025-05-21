import feedparser
import requests
from datetime import datetime

RSS_URL = 'https://www.federalreserve.gov/feeds/press_meetings.xml'

def fetch_fomc_minutes() -> dict:
    d = feedparser.parse(RSS_URL)
    entry = next((e for e in d.entries if 'Minutes' in e.title), None)
    if not entry:
        return {"timestamp": datetime.utcnow().isoformat(), "error": "No minutes found"}
    link = entry.link
    resp = requests.get(link, timeout=10)
    text = resp.text
    return {
        "title": entry.title,
        "link": link,
        "text": text,
        "timestamp": datetime.utcnow().isoformat()
    }
