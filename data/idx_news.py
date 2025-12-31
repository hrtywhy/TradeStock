
from curl_cffi import requests
import datetime
import json

class IDXNewsFetcher:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://idx.co.id/id/perusahaan-tercatat/keterbukaan-informasi/",
            "Origin": "https://idx.co.id"
        }

    def get_stock_news(self, symbol_jk, days=30):
        """
        Fetches news and announcements for a specific stock (e.g. BBRI.JK).
        Combines results from 'Keterbukaan Informasi' and 'Berita'.
        Returns a list of strings: ["Title - Date", ...]
        """
        symbol = symbol_jk.replace(".JK", "")
        news_items = []
        
        # Date filter (Default 30 days to catch monthly announcements)
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days)
        
        # Format for IDX API (YYYYMMDD for Announcement, YYYY-MM-DD sometimes for others)
        d_from_str = start_date.strftime("%Y%m%d")
        d_to_str = end_date.strftime("%Y%m%d")

        # 1. Fetch Keterbukaan Informasi (Official Announcements)
        try:
            url_announce = "https://idx.co.id/primary/ListedCompany/GetAnnouncement"
            params_ann = {
                "kodeEmiten": symbol,
                "emitenType": "*",
                "indexFrom": 0,
                "pageSize": 5, # Top 5 latest
                "dateFrom": d_from_str,
                "dateTo": d_to_str,
                "lang": "id",
                "keyword": ""
            }
            # Use curl_cffi to impersonate Chrome and bypass 403
            r = requests.get(url_announce, params=params_ann, headers=self.headers, impersonate="chrome120", timeout=15)
            



            if r.status_code == 200:
                data = r.json()
                if "Replies" in data and data["Replies"]:
                    for item in data["Replies"]:
                        p = item.get("pengumuman", {})
                        title = p.get("JudulPengumuman", "")
                        date = p.get("TglPengumuman", "")[:10]
                        if title:
                            news_items.append(f"[Official] {date} - {title}")
                # else: pass (silently)
            else:
                print(f"[IDX Debug] Announcement API failed: {r.status_code}")
        except Exception as e:
            print(f"[IDX News] Error fetching announcements for {symbol}: {e}")

        # 2. Fetch Berita (General News Filtered by Keyword)
        try:
            url_news = "https://idx.co.id/primary/NewsAnnouncement/GetNewsSearch"
            params_news = {
                "locale": "id-id",
                "pageNumber": 1,
                "pageSize": 5,
                "keyword": symbol,
                "dateFrom": start_date.strftime("%Y-%m-%d"),
                "dateTo": end_date.strftime("%Y-%m-%d")
            }
            r = requests.get(url_news, params=params_news, headers=self.headers, impersonate="chrome120", timeout=15)
            
            if r.status_code == 200:
                data = r.json()
                if "Items" in data and data["Items"]:
                    for item in data["Items"]:
                        title = item.get("Title", "")
                        news_items.append(f"[News] {title}")
        except Exception as e:
            print(f"[IDX News] Error fetching news for {symbol}: {e}")

        return news_items
