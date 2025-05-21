import requests
import os
from datetime import datetime

def fetch_pce_data(api_key: str = None) -> dict:
    api_key = api_key or os.getenv('BEA_API_KEY')
    base = "https://apps.bea.gov/api/data"
    params = {
        "UserID": api_key,
        "method": "GetData",
        "datasetname": "NIPA",
        "TableName": "T20305",
        "Frequency": "M",
        "Year": "ALL"
    }
    resp = requests.get(base, params=params, timeout=10)
    js = resp.json()
    data = js["BEAAPI"]["Results"]["Data"]
    pce_series = [d for d in data if d["LineDescription"] == "PCE Price Index"]
    core_series = [d for d in data if d["LineDescription"] == "PCE Price Index Excluding Food and Energy"]
    last2_pce = pce_series[-2:]
    last2_core = core_series[-2:]
    def mom(arr):
        v0 = float(arr[0]["DataValue"])
        v1 = float(arr[1]["DataValue"])
        return round((v1 - v0) / v0 * 100, 2)
    return {
        "pce_mom": mom(last2_pce),
        "core_pce_mom": mom(last2_core),
        "timestamp": datetime.utcnow().isoformat()
    }
