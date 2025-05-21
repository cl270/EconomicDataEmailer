import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

def fetch_case_shiller() -> dict:
    url = os.getenv('CASE_SHILLER_URL', 'https://us.spindices.com/indices/real-estate/sp-case-shiller-us-national-home-price-index')
    resp = requests.get(url, timeout=10)
    soup = BeautifulSoup(resp.text, 'html.parser')
    elem = soup.find(class_='index-value')
    value = elem.get_text(strip=True) if elem else None
    return {"case_shiller_index": value, "timestamp": datetime.utcnow().isoformat()}
