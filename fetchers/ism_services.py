import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

def fetch_ism_services() -> dict:
    url = os.getenv('ISM_SERVICES_URL', 'https://www.ismworld.org/globalassets/pub/research-and-surveys/rob/pmi/current/rob0515.html')
    resp = requests.get(url, timeout=10)
    soup = BeautifulSoup(resp.text, 'html.parser')
    elem = soup.find(class_='pmi-value')
    value = elem.get_text(strip=True) if elem else None
    return {"services_pmi": value, "timestamp": datetime.utcnow().isoformat()}
