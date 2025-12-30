import yfinance as yf
import pandas as pd
import time

def fetch_data(symbol, period="1y", interval="1d"):
    """
    Fetches historical OHLCV data for a given symbol from Yahoo Finance.
    
    Args:
        symbol (str): Ticker symbol (e.g., 'BBCA.JK')
        period (str): Data period to download (default: '1y')
        interval (str): Data interval (default: '1d')
        
    Returns:
        pd.DataFrame: DataFrame containing Date, Open, High, Low, Close, Volume.
                      Returns None if data is invalid or empty.
    """
    try:
        # yfinance download
        # auto_adjust=True to handle dividends/splits roughly equivalent to adjusted close
        df = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=False)
        
        if df.empty:
            print(f"Warning: No data found for {symbol}")
            return None
            
        # Ensure MultiIndex columns are handled if yfinance returns them (common in recent versions)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        # Required columns check
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in df.columns for col in required_cols):
             # Try mapping commonly found alternative names if necessary, 
             # but yfinance standardizes to Title Case usually.
             print(f"Warning: Missing columns for {symbol}. Found: {df.columns}")
             return None
             
        df = df[required_cols]
        df.dropna(inplace=True)
        
        return df

    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

def get_latest_news(symbol):
    """
    Fetches the latest news headline for the symbol.
    """
    try:
        t = yf.Ticker(symbol)
        news = t.news
        if news:
            return news[0]['title']
    except:
        pass
    return "No recent news found."

def get_last_price(symbol):
    """
    Quickly fetch the latest live price (delayed) if needed, 
    though strategy mainly uses EOD close.
    """
    try:
        ticker = yf.Ticker(symbol)
        # fast_info is often faster than history for just current price
        return ticker.fast_info['last_price']
    except:
        return None
