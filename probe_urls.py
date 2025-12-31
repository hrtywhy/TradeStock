import requests

urls = [
    "https://raw.githubusercontent.com/wildangunawan/Dataset-Saham-IDX/master/stock.csv",
    "https://raw.githubusercontent.com/wildangunawan/Dataset-Saham-IDX/master/stock.json",
    "https://raw.githubusercontent.com/wildangunawan/Dataset-Saham-IDX/master/companies.csv",
    "https://raw.githubusercontent.com/goapi-id/co_id_stocks_list/master/symbols.txt",
    "https://raw.githubusercontent.com/brisaham/idx-stock-list/main/stock_list.csv"
]

for url in urls:
    try:
        r = requests.get(url)
        if r.status_code == 200:
            print(f"FOUND: {url}")
            print(r.text[:200])
        else:
            print(f"Stats {r.status_code} for {url}")
    except:
        pass
