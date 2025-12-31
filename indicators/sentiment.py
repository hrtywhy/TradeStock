
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

def get_market_sentiment(symbol):
    """
    Fetches news for a symbol and uses Gemini to analyze sentiment.
    Returns a score from -100 (Bearish) to +100 (Bullish).
    """
    if not config.GENAI_API_KEY:
        print("[WARN] GENAI_API_KEY not set. Skipping sentiment analysis.")
        return 0, "No API Key"

    try:
        # 1. Fetch News via yfinance
        # Note: yf news is often general. For IDX, we might get limited results.
        # We append '.JK' for Yahoo Finance
        ticker = yf.Ticker(symbol)
        news_list = ticker.news
        
        if not news_list:
            return 0, "No News Found"
            
        headlines = []
        for item in news_list[:5]: # Analyze top 5 recent news
            title = item.get('title', '')
            link = item.get('link', '')
            # Filter for recent news only (last 7 days) if possible
            # But yfinance news doesn't always have easy date parsing, so we take latest.
            headlines.append(f"- {title}")
            
        if not headlines:
            return 0, "No Headlines"




        news_text = "\n".join(headlines)
        
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
