import requests

urls = [
    "https://raw.githubusercontent.com/wildangunawan/Dataset-Saham-IDX/main/stock.csv",
    "https://raw.githubusercontent.com/wildangunawan/Dataset-Saham-IDX/main/info.json", 
    "https://raw.githubusercontent.com/wildangunawan/Dataset-Saham-IDX/main/companies.csv",
    "https://raw.githubusercontent.com/goapi-id/co_id_stocks_list/main/symbols.txt"
]

for url in urls:
    try:
        r = requests.get(url)
        if r.status_code == 200:
            print(f"FOUND: {url}")
        else:
            print(f"Stats {r.status_code} for {url}")
    except:
        pass
