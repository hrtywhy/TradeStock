import requests
import json
import os
import datetime

# Cache file to store the universe so we don't spam the source
CACHE_FILE = "data/idx_universe_cache.json"
CACHE_DURATION_DAYS = 1

def fetch_idx_universe():
    """
    Fetches the list of all IDX stocks from a reliable public source.
    Returns a list of symbols in Yahoo Finance format (e.g., 'BBCA.JK').
    """
    # Check cache first
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                data = json.load(f)
                last_update = datetime.datetime.fromisoformat(data['last_updated'])
                if (datetime.datetime.now() - last_update).days < CACHE_DURATION_DAYS:
                    print(f"[UNIVERSE] Loaded {len(data['symbols'])} stocks from cache.")
                    return data['symbols']
        except Exception as e:
            print(f"[UNIVERSE] Cache read error: {e}")

    # Source: nichsedge/idx-bei GitHub repo (Reliable JSON source of IDX companies)
    # This is often updated and provides a clean list of tickers.
    url = "https://raw.githubusercontent.com/nichsedge/idx-bei/master/data/companyDetailsByKodeEmiten.json"
    
    print("[UNIVERSE] Fetching latest IDX stock list...")
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            # Extract keys (tickers) and append .JK
            symbols = [f"{ticker}.JK" for ticker in data.keys()]
            
            # Save to cache
            with open(CACHE_FILE, 'w') as f:
                json.dump({
                    "last_updated": datetime.datetime.now().isoformat(),
                    "symbols": symbols
                }, f)
                
            print(f"[UNIVERSE] Successfully fetched {len(symbols)} stocks.")
            return symbols
        else:
            print(f"[UNIVERSE] Error fetching data: Status {r.status_code}")
            return []
            
    except Exception as e:
        print(f"[UNIVERSE] Fetch failed: {e}")
        return []

if __name__ == "__main__":
    s = fetch_idx_universe()
    print(s[:10])
