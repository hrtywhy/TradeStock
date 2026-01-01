
import os
import google.generativeai as genai
import yfinance as yf
from datetime import datetime, timedelta
import sys

# Add parent to path for config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Configure Gemini
if config.GENAI_API_KEY:
    genai.configure(api_key=config.GENAI_API_KEY)


from data.idx_news import IDXNewsFetcher
from data.external_news import FinnhubNewsFetcher, PolygonNewsFetcher, MarketAuxFetcher, NewsAPIFetcher, NewsDataFetcher

# Init Fetchers
idx_fetcher = IDXNewsFetcher()
finnhub_fetcher = FinnhubNewsFetcher()
polygon_fetcher = PolygonNewsFetcher()
marketaux_fetcher = MarketAuxFetcher()
newsapi_fetcher = NewsAPIFetcher()
newsdata_fetcher = NewsDataFetcher()

def get_market_sentiment(symbol):
    """
    Fetches news for a symbol (from IDX, Finnhub, Polygon, MarketAux, NewsAPI, NewsData) and uses Gemini to analyze sentiment.
    Returns a score from -100 (Bearish) to +100 (Bullish).
    """
    if not config.GENAI_API_KEY:
        print("[WARN] GENAI_API_KEY not set. Skipping sentiment analysis.")
        return 0, "No API Key"

    try:
        # 1. Fetch News from IDX (Official Sources)
        headlines = idx_fetcher.get_stock_news(symbol, days=7)
        if headlines is None:
            headlines = []
            
        # 2. Fetch News from Finnhub
        fh_headlines = finnhub_fetcher.get_company_news(symbol, days=7)
        if fh_headlines:
             headlines.extend(fh_headlines)
            
        # 3. Fetch News from Polygon
        poly_headlines = polygon_fetcher.get_company_news(symbol, limit=5)
        if poly_headlines:
             headlines.extend(poly_headlines)
        
        # 4. Fetch News from MarketAux
        ma_headlines = marketaux_fetcher.get_company_news(symbol, limit=3)
        if ma_headlines:
             headlines.extend(ma_headlines)

        # 5. Fetch News from NewsAPI
        na_headlines = newsapi_fetcher.get_company_news(symbol, days=7)
        if na_headlines:
             headlines.extend(na_headlines)

        # 6. Fetch News from NewsData
        nd_headlines = newsdata_fetcher.get_company_news(symbol, limit=3)
        if nd_headlines:
             headlines.extend(nd_headlines)
        
        # Fallback to yfinance if all else fails
        if not headlines:
             ticker = yf.Ticker(symbol)
             if ticker.news:
                 headlines = [f"[Yahoo] {item.get('title')}" for item in ticker.news[:3]]
            
        if not headlines:
            return 0, "No Headlines Found"

        news_text = "\n".join(headlines[:30]) # Increased limit to 30 for massive input

        
        # 2. Ask Gemini
        # Using the latest stable flash model
        model_name = 'gemini-flash-latest'
        try:
             model = genai.GenerativeModel(model_name)
        except:
             # Fallback
             model = genai.GenerativeModel('gemini-pro')
             
        prompt = f"""
        Analyze the sentiment of the following news headlines for the stock '{symbol}'.
        Headlines:
        {news_text}
        
        Output format:
        SCORE: [Integer from -100 to 100]
        SUMMARY:
        (+) [Positive news point]
        (-) [Negative news point]
        
        Rules:
        - Score: -100 (Bankruptcy/Crash) to +100 (Growth/Dividends). 0 if Neutral.
        - Summary: List top 1-2 positive (+) and/or top 1-2 negative (-) points derived from headlines.
        - If no positive/negative news, omit that line.
        """
        
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Parse Score
        try:
            import re
            score_match = re.search(r"SCORE:\s*([-]?\d+)", text)
            if score_match:
                score = int(score_match.group(1))
            else:
                 # Fallback greedy find
                 score = int(''.join(filter(lambda x: x.isdigit() or x == '-', text.split('\n')[0])))
        except:
            score = 0
            
        # Parse Summary
        summary_match = re.search(r"SUMMARY:(.*)", text, re.DOTALL)
        if summary_match:
            explanation = summary_match.group(1).strip()
        else:
            explanation = "News analysis available but formatting failed."

        # Clamp score
        score = max(-100, min(100, score))
        
        return score, explanation

    except Exception as e:
        print(f"[ERROR] Sentiment Analysis Failed: {e}")
        return 0, str(e)
