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
        # Use Ticker.history which is often more reliable for single requests
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval, auto_adjust=False)
        
        if df.empty:
            # Fallback: sometimes history returns empty if auto_adjust is False for some reason, try default
            df = ticker.history(period=period, interval=interval)
            
        if df.empty:
            print(f"Warning: No data found for {symbol}")
            return None
            
        # Ensure MultiIndex columns are handled
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        # Standardize columns
        df.reset_index(inplace=True) # Ensure Date is a column if it's in index
        
        # Determine Date column (sometimes 'Date' or 'Datetime')
        date_col = 'Date' if 'Date' in df.columns else 'Datetime'
        
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        
        # Check if we have what we need
        if not all(col in df.columns for col in required_cols):
             print(f"Warning: Missing columns for {symbol}. Found: {df.columns}")
             return None
             
        # Set index back to Date for strategy compatibility
        if date_col in df.columns:
            df.set_index(date_col, inplace=True)
            
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
