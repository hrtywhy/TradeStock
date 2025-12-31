import requests
import json

def fetch_nichsedge():
    url = "https://raw.githubusercontent.com/nichsedge/idx-bei/master/data/companyDetailsByKodeEmiten.json"
    try:
        r = requests.get(url)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Found {len(data)} tickers.")
            print(list(data.keys())[:5])
    except Exception as e:
        print(e)
        
if __name__ == "__main__":
    fetch_nichsedge()
