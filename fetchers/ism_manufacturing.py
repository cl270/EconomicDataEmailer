import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

def fetch_ism_manufacturing() -> dict:
    url = os.getenv('ISM_MANUFACTURING_URL', 'https://www.ismworld.org/globalassets/pub/research-and-surveys/rob/pmi/current/pmi0515.html')
    resp = requests.get(url, timeout=10)
    soup = BeautifulSoup(resp.text, 'html.parser')
    elem = soup.find(class_='pmi-value')
    value = elem.get_text(strip=True) if elem else None
    return {"manufacturing_pmi": value, "timestamp": datetime.utcnow().isoformat()}
