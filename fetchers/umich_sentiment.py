import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

def fetch_umich_sentiment() -> dict:
    url = os.getenv('UMICH_URL', 'https://data.sca.isr.umich.edu/fetchdoc.php?docid=wd-2025-05-16')
    resp = requests.get(url, timeout=10)
    soup = BeautifulSoup(resp.text, 'html.parser')
    elem = soup.find(id='surveyvalue')
    value = elem.get_text(strip=True) if elem else None
    return {"consumer_sentiment": value, "timestamp": datetime.utcnow().isoformat()}
