import requests
from datetime import datetime

def fetch_nfp_data() -> dict:
    sid = 'CES0000000001'
    url = f"https://api.bls.gov/publicAPI/v2/timeseries/data/{sid}?latest=true"
    resp = requests.get(url, timeout=5)
    js = resp.json()
    data = js["Results"]["series"][0]["data"]
    if len(data) >= 2:
        curr = int(data[0]["value"].replace(',', ''))
        prev = int(data[1]["value"].replace(',', ''))
        change = curr - prev
    else:
        change = None
    return {"nfp_change": change, "timestamp": datetime.utcnow().isoformat()}
