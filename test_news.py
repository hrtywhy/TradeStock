
import config
from indicators.sentiment import get_market_sentiment
from data.idx_news import IDXNewsFetcher


def test_news_deep_dive():
    symbol = "BBRI.JK" # Bank Rakyat Indonesia
    print(f"--- Testing Deep Research for {symbol} ---")
    
    # 1. Raw Fetch
    fetcher = IDXNewsFetcher()
    print("\n[1] Fetching Raw News from IDX (Announcements + Search)...")
    headlines = fetcher.get_stock_news(symbol)
    if headlines:
        print(f"    [OK] Found {len(headlines)} items:")
        for h in headlines:
            print(f"         - {h}")
    else:
        print("    [X] No headlines found. (Check API or Stock Code)")
        
    # 2. Sentiment Analysis (Gemini)
    print("\n[2] Running Gemini Sentiment Analysis...")
    score, reason = get_market_sentiment(symbol)
    print(f"    Score   : {score}")
    print(f"    Analysis: {reason}")
    

    if score != 0 and reason != "No Headlines Found":
        print("\n[OK] Deep Research System: OPERATIONAL")
    else:
        print("\n[WARN] Deep Research System: NO DATA/ERROR")

if __name__ == "__main__":
    test_news_deep_dive()
