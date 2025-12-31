import requests
import json

def fetch_idx_official():
    # Attempt 1: Old IDX API (often still works for backends)
    url = "https://www.idx.co.id/primary/Json/GetEmiten?indexFrom=1&pageSize=1000&year=2024&month=12"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            # print(data) # It might be big
            if 'Replies' in data:
                count = len(data['Replies'])
                print(f"Found {count} tickers from IDX Official.")
                if count > 0:
                     print(f"First: {data['Replies'][0]['KodeEmiten']}")
            else:
                print("JSON structure unknown")
                print(str(data)[:200])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_idx_official()
