import requests
from datetime import datetime

BASE_URL = 'https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query'

def fetch_latest_auction_results() -> dict:
    params = {'$top': 1, 'sort': '-auction_date'}
    resp = requests.get(BASE_URL, params=params, timeout=10)
    data = resp.json().get('data', [])
    if not data:
        return {"timestamp": datetime.utcnow().isoformat(), "error": "No data"}
    result = data[0]
    return {
        "auction_date": result.get('auction_date'),
        "security_type": result.get('security_type'),
        "high_rate": result.get('high_rate'),
        "bid_to_cover": result.get('bid_to_cover'),
        "timestamp": datetime.utcnow().isoformat()
    }
