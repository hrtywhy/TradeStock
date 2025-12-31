
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

# Init Fetcher
idx_fetcher = IDXNewsFetcher()

def get_market_sentiment(symbol):
    """
    Fetches news for a symbol (from IDX Official) and uses Gemini to analyze sentiment.
    Returns a score from -100 (Bearish) to +100 (Bullish).
    """
    if not config.GENAI_API_KEY:
        print("[WARN] GENAI_API_KEY not set. Skipping sentiment analysis.")
        return 0, "No API Key"

    try:
        # 1. Fetch News from IDX (Official Sources)
        headlines = idx_fetcher.get_stock_news(symbol, days=7)
        
        # Fallback to yfinance if IDX returns nothing (rare but possible)
        if not headlines:
             ticker = yf.Ticker(symbol)
             if ticker.news:
                 headlines = [f"[Yahoo] {item.get('title')}" for item in ticker.news[:3]]
            
        if not headlines:
            return 0, "No Headlines Found"

        news_text = "\n".join(headlines[:10]) # Limit input length
        
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
        
        Provide a Sentiment Score from -100 (Extremely Negative/Bankruptcy risk) to +100 (Extremely Positive/Growth/Dividends).
        0 is Neutral.
        Return ONLY the number.
        """
        
        response = model.generate_content(prompt)
        score_text = response.text.strip()
        
        # Clean up response to get just the integer
        try:
            score = int(''.join(filter(lambda x: x.isdigit() or x == '-', score_text)))
        except:
            score = 0
            
        # Clamp score
        score = max(-100, min(100, score))
        
        explanation = f"Based on {len(headlines)} headlines."
        return score, explanation

    except Exception as e:
        print(f"[ERROR] Sentiment Analysis Failed: {e}")
        return 0, str(e)
