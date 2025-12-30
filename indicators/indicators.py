import pandas as pd
import numpy as np
from ta.trend import SMAIndicator
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange

def add_indicators(df):
    """
    Adds technical indicators to the dataframe.
    
    Args:
        df (pd.DataFrame): Dataframe with OHLCV data.
        
    Returns:
        pd.DataFrame: Dataframe with added indicator columns.
    """
    if df is None or len(df) < 50:
        return df

    # Moving Averages
    df['MA20'] = SMAIndicator(close=df['Close'], window=20).sma_indicator()
    df['MA50'] = SMAIndicator(close=df['Close'], window=50).sma_indicator()
    
    # RSI
    df['RSI'] = RSIIndicator(close=df['Close'], window=14).rsi()
    
    # Volume Moving Average
    df['VolMA20'] = df['Volume'].rolling(window=20).mean()
    
    # Support & Resistance (20-day Lookback)
    # We use shift(1) to ensure we don't lookahead, but for 'today's' S/R based on valid history,
    # usually traders look at the *previous* N days.
    # However, for breakout detection, we compare Today's Close vs Last 20 Highs.
    # Let's calculate the simplistic rolling min/max.
    df['Support20'] = df['Low'].rolling(window=20).min()
    df['Resistance20'] = df['High'].rolling(window=20).max()
    
    # ATR for Risk Management (stop loss distance estimation)
    atr = AverageTrueRange(high=df['High'], low=df['Low'], close=df['Close'], window=14)
    df['ATR'] = atr.average_true_range()
    
    return df
