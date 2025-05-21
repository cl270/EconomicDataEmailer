import requests
from datetime import datetime

def fetch_cpi_data() -> dict:
    series = {
        "CPI": "CUSR0000SA0",
        "CoreCPI": "CUSR0000SA0L1E"
    }
    results = {}
    for name, sid in series.items():
        url = f"https://api.bls.gov/publicAPI/v2/timeseries/data/{sid}?latest=true"
        resp = requests.get(url, timeout=5)
        js = resp.json()
        data = js["Results"]["series"][0]["data"]
        if len(data) >= 2:
            val = float(data[0]["value"])
            prev = float(data[1]["value"])
            mom = (val - prev) / prev * 100
            results[name] = round(mom, 2)
            if len(data) > 2:
                prev2 = float(data[2]["value"])
                results[f"prev_{name}"] = round((prev - prev2) / prev2 * 100, 2)
            else:
                results[f"prev_{name}"] = None
        else:
            results[name] = None
            results[f"prev_{name}"] = None
    return {
        "cpi_mom": results["CPI"],
        "core_cpi_mom": results["CoreCPI"],
        "prev_CPI": results["prev_CPI"],
        "prev_CoreCPI": results["prev_CoreCPI"],
        "timestamp": datetime.utcnow().isoformat()
    }
