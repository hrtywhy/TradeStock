import finnhub
from polygon import RESTClient
import requests
import os
import sys
from datetime import datetime, timedelta

# Add parent to path for config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class FinnhubNewsFetcher:
    def __init__(self):
        self.api_key = config.FINNHUB_API_KEY
        self.client = None
        if self.api_key:
            try:
                self.client = finnhub.Client(api_key=self.api_key)
            except Exception as e:
                print(f"[Finnhub] Error initializing client: {e}")

    def get_company_news(self, symbol, days=7):
        """
        Fetches company news from Finnhub.
        """
        if not self.client:
            return []
        
        # Calculate date range
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        headlines = []
        try:
            # Finnhub Company News
            news = self.client.company_news(symbol, _from=start_date, to=end_date)
            
            if news:
                for item in news:
                    headline = item.get('headline')
                    summary = item.get('summary', '')
                    source = item.get('source', 'Finnhub')
                    
                    full_text = f"[{source}] {headline}: {summary}"
                    headlines.append(full_text)
                    
        except Exception as e:
            print(f"[Finnhub] Error fetching news for {symbol}: {e}")

        return headlines

class PolygonNewsFetcher:
    def __init__(self):
        self.api_key = config.POLYGON_API_KEY
        self.client = None
        if self.api_key:
            try:
                self.client = RESTClient(api_key=self.api_key)
            except Exception as e:
                print(f"[Polygon] Error initializing client: {e}")

    def get_company_news(self, symbol, limit=10):
        """
        Fetches ticker news from Polygon.io.
        """
        if not self.client:
            return []
            
        headlines = []
        try:
            # Polygon handles tickers usually without market suffix for US, 
            # but for non-US it might differ. 
            # We will try exact symbol first. If it is an IDX stock 'UNTR.JK', 
            # Polygon might not track it well or use different ID.
            # However, for global stocks or if they map it, it works.
            # Polygon mainly covers US market but has some global coverage.
            # We attempt the exact symbol. 
            
            # Note: Polygon requires 'ticker' param.
            # If symbol has .JK, we might try stripping it if no results, 
            # but stripping it maps to US ticker (e.g. UNTR.JK -> UNTR might be US stock).
            # So we stick to exact first.
            
            response = self.client.list_ticker_news(ticker=symbol, limit=limit)
            
            # Response is a generator/iterator in some ver, or list
            for item in response:
                 title = getattr(item, 'title', '')
                 description = getattr(item, 'description', '')
                 author = getattr(item, 'author', 'Polygon')
                 
                 full_text = f"[{author}] {title}: {description}"
                 headlines.append(full_text)
                 
        except Exception as e:
            # Polygon might return 404 or empty if not found
            # print(f"[Polygon] Note: {e}") 
            pass

        return headlines

class MarketAuxFetcher:
    def __init__(self):
        self.api_key = config.MARKETAUX_API_KEY
    
    def get_company_news(self, symbol, limit=3):
        if not self.api_key:
            return []
        
        try:
            url = "https://api.marketaux.com/v1/news/all"
            params = {
                'symbols': symbol,
                'filter_entities': 'true',
                'limit': limit,
                'api_token': self.api_key,
                'language': 'en'
            }
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                headlines = []
                for item in data.get('data', []):
                    title = item.get('title')
                    desc = item.get('description', '')
                    source = item.get('source')
                    headlines.append(f"[MarketAux-{source}] {title}: {desc}")
                return headlines
        except Exception as e:
            print(f"[MarketAux] Exception: {e}")
        return []

class NewsAPIFetcher:
    def __init__(self):
        self.api_key = config.NEWSAPI_KEY

    def get_company_news(self, symbol, days=7):
        if not self.api_key:
            return []
        
        try:
            url = "https://newsapi.org/v2/everything"
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            params = {
                'q': symbol,
                'from': start_date,
                'sortBy': 'publishedAt',
                'apiKey': self.api_key,
                'language': 'en' 
            }
            response = requests.get(url, params=params, timeout=10)
             
            if response.status_code == 200:
                data = response.json()
                headlines = []
                for item in data.get('articles', [])[:5]:
                    title = item.get('title')
                    desc = item.get('description', '')
                    source = item.get('source', {}).get('name')
                    headlines.append(f"[NewsAPI-{source}] {title}: {desc}")
                return headlines
        except Exception as e:
            print(f"[NewsAPI] Exception: {e}")
        return []

class NewsDataFetcher:
    def __init__(self):
        self.api_key = config.NEWSDATA_KEY
    
    def get_company_news(self, symbol, limit=5):
        if not self.api_key:
            return []
            
        try:
            url = "https://newsdata.io/api/1/news"
            params = {
                'apikey': self.api_key,
                'q': symbol,
                'language': 'en,id' 
            }
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                headlines = []
                for item in data.get('results', [])[:limit]:
                    title = item.get('title')
                    desc = item.get('description', '')
                    if desc is None: desc = ""
                    source = item.get('source_id')
                    headlines.append(f"[NewsData-{source}] {title}: {desc}")
                # Rate limit safety
                if data.get('totalResults', 0) > 0:
                     pass
                return headlines
        except Exception as e:
             print(f"[NewsData] Exception: {e}")
        return []
