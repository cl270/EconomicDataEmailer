import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

def fetch_existing_home_sales() -> dict:
    url = os.getenv('NAR_EXISTING_URL', 'https://www.nar.realtor/research-and-statistics/housing-statistics/existing-home-sales')
    resp = requests.get(url, timeout=10)
    soup = BeautifulSoup(resp.text, 'html.parser')
    elem = soup.find(class_='nar-hs-stats-value')
    value = elem.get_text(strip=True) if elem else None
    return {"existing_home_sales": value, "timestamp": datetime.utcnow().isoformat()}

def fetch_new_home_sales() -> dict:
    base = 'https://api.census.gov/data/timeseries/eits/ressales'
    params = {'get': 'year,period,seasonally_adjusted_rate', 'time': 'latest'}
    resp = requests.get(base, params=params, timeout=10)
    data = resp.json()
    year, period, rate = data[1]
    return {
        "new_home_sales_year": year,
        "new_home_sales_period": period,
        "new_home_sales_rate": rate,
        "timestamp": datetime.utcnow().isoformat()
    }
