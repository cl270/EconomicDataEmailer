import requests
from datetime import datetime, timedelta
import pytz

# ------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------

# The TradingView Economic Calendar JSON endpoint
API_URL = "https://economic-calendar.tradingview.com/events"

# Must supply an Origin header or you'll get a 403
HEADERS = {
    "Origin": "https://in.tradingview.com"
}

# Country filter
COUNTRIES = ["US"]

# How far ahead to fetch (days)
DAYS_AHEAD = 30

# Substrings to match the events you care about
KEYWORDS = [
    "Jobless Claims",
    "Home Sales",
    "Bill Auction",
    "Note Auction",
    "Bond Auction",
    "Fed Interest Rate Decision",
    "FOMC Meeting Minutes",
    "PCE Price Index",
    "Core PCE",
    "Consumer Price Index",
    "Core Consumer Price Index",
    "Michigan Consumer Sentiment",
    "Manufacturing PMI",
    "Services PMI",
    "Nonfarm Payrolls",
]

# Timezones
UTC = pytz.UTC
ET = pytz.timezone("US/Eastern")


# ------------------------------------------------------------------
# FETCH + PARSE LOGIC
# ------------------------------------------------------------------

def fetch_tradingview_calendar(days_ahead: int = DAYS_AHEAD, countries=None):
    """
    Fetch raw JSON from TradingView for the given date window and countries.
    Returns the 'result' list from the payload.
    """
    countries = countries or COUNTRIES
    now = datetime.utcnow()
    params = {
        # TradingView expects ISO8601 ending in 'Z' for UTC
        "from": now.isoformat() + "Z",
        "to": (now + timedelta(days=days_ahead)).isoformat() + "Z",
        "countries": ",".join(countries),
    }
    resp = requests.get(API_URL, headers=HEADERS, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json().get("result", [])


def parse_tradingview_events(raw_events, keywords=None, debug=False):
    """
    From raw_events (list of dicts), keep only those whose 'title'
    contains any of the substrings in keywords. Convert 'date' to
    timezone‐aware datetime objects.
    Returns a list of dicts:
      {
        'indicator': str,
        'datetime_et': datetime,
        'actual': str|None,
        'forecast': str|None,
        'previous': str|None,
        'url': str
      }
    """
    keywords = [k.lower() for k in (keywords or KEYWORDS)]
    out = []

    for ev in raw_events:
        title = ev.get("title", "")
        country = ev.get("country", "")
        # filter country and keyword
        if country.upper() != "US":
            continue
        if not any(kw in title.lower() for kw in keywords):
            continue

        # parse the UTC timestamp
        # TradingView returns 'date' like "2025-06-05T08:30:00"
        # or "2025-06-05 08:30:00" – we normalize to isoformat
        date_str = ev.get("date", "")
        if not date_str:
            continue

        # Normalize to ISO
        ds = date_str.replace(" ", "T")
        try:
            # Assume UTC if no offset
            dt_utc = datetime.fromisoformat(ds)
            dt_utc = dt_utc.replace(tzinfo=UTC)
        except ValueError:
            if debug:
                print("Failed to parse date:", ds)
            continue

        # Convert to Eastern
        dt_et = dt_utc.astimezone(ET)

        entry = {
            "indicator": title,
            "datetime_et": dt_et,
            "actual": ev.get("actual") or None,
            "forecast": ev.get("forecast") or None,
            "previous": ev.get("previous") or None,
            "url": f"https://tradingeconomics.com{ev.get('URL', '')}"  # tradingeconomics? no, tradingview uses 'url'?
                   or ev.get("url")  # some entries use 'url' key
        }

        out.append(entry)

        if debug:
            print("MATCHED:", title)
            print("  ET:", dt_et.isoformat(),
                  "Actual:", entry["actual"],
                  "Fcst:", entry["forecast"],
                  "Prev:", entry["previous"])
            print("---")

    if debug:
        print(f"Total raw events: {len(raw_events)}, Matched: {len(out)}\n")

    return out


def get_tradingview_releases(days_ahead: int = DAYS_AHEAD, debug=False):
    """
    Fetch & parse upcoming releases from TradingView.
    Returns only entries whose datetime_et >= now.
    """
    raw = fetch_tradingview_calendar(days_ahead)
    parsed = parse_tradingview_events(raw, debug=debug)
    now_et = datetime.now(ET)
    upcoming = [e for e in parsed if e["datetime_et"] >= now_et]

    if debug:
        print("now (ET):", now_et.isoformat())
        print("upcoming count:", len(upcoming), "\n")

    return upcoming


# ------------------------------------------------------------------
# QUICK TEST
# ------------------------------------------------------------------

if __name__ == "__main__":
    # Turn on debug=True to see exactly what's fetched & matched
    events = get_tradingview_releases(days_ahead=7, debug=True)
    for e in events:
        print(f"{e['datetime_et']} — {e['indicator']}")
        print(f"  Actual:   {e['actual']}")
        print(f"  Forecast: {e['forecast']}")
        print(f"  Previous: {e['previous']}")
        print(f"  URL:      {e['url']}\n")
