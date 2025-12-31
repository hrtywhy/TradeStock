import requests
import json

def get_idx_tickers():
    url = "https://query2.finance.yahoo.com/v1/finance/screener?lang=en-US&region=US&corsDomain=finance.yahoo.com"
    
    # Payload to fetch all equity for region 'id' (Indonesia)
    # We might need to iterate if count > 250
    tickers = []
    offset = 0
    size = 250
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    while True:
        params = {
            "scrIds": "all_stocks", # generic screener
            "count": size,
            "offset": offset,
            "formatted": "false",
            "corsDomain": "finance.yahoo.com"
        }
        # Actually, the GET request for predefined screeners is different from custom query.
        # Let's try the POST method which is more powerful for filtering by region.
        
        post_url = "https://query2.finance.yahoo.com/v1/finance/screener"
        payload = {
            "size": size,
            "offset": offset, 
            "sortField": "intradaymarketcap",
            "sortType": "DESC",
            "quoteType": "EQUITY",
            "topOperator": "AND",
            "query": {
                "operator": "AND",
                "operands": [
                    {"operator": "EQ", "operands": ["region", "id"]},
                    {"operator": "EQ", "operands": ["exchange", "JKT"]} # Jakarta Stock Exchange
                ]
            }
        }
        
        try:
            r = requests.post(post_url, json=payload, headers=headers)
            data = r.json()
            
            if 'finance' not in data or 'result' not in data['finance']:
                print("Error in response structure")
                break
                
            quotes = data['finance']['result'][0]['quotes']
            if not quotes:
                break
                
            for q in quotes:
                if 'symbol' in q:
                    tickers.append(q['symbol'])
            
            if len(quotes) < size:
                break
                
            offset += size
            print(f"Fetched {len(tickers)} so far...")
            
        except Exception as e:
            print(f"Error: {e}")
            break
            
    return tickers

if __name__ == "__main__":
    t = get_idx_tickers()
    print(f"Total Found: {len(t)}")
    print(f"Sample: {t[:10]}")
