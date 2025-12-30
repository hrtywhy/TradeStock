import pandas as pd
import sys
import os

# Add parent directory to path to import config if needed, though we passed params usually
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_swing_setup(df):
    """
    Analyzes the latest candle in the dataframe against the Swing Strategy rules.
    
    Rules (AND Logic):
    1. Trend: Close > MA50 and MA20 > MA50
    2. Setup: RSI between 45 and 55
    3. Volume: Volume > VolMA20
    
    Args:
        df (pd.DataFrame): Dataframe with indicators populated.
        
    Returns:
        dict: Signal result containing status, decision, and meta-data.
    """
    if df is None or len(df) < 50:
        return {"valid": False, "reason": "Insufficient Data"}

    # Get the latest confirmed candle (last row)
    curr = df.iloc[-1]
    
    # Extract values
    close = curr['Close']
    ma20 = curr['MA20']
    ma50 = curr['MA50']
    rsi = curr['RSI']
    vol = curr['Volume']
    vol_ma = curr['VolMA20']
    atr = curr['ATR']
    support = curr['Support20']
    resistance = curr['Resistance20']
    
    # 1. Trend Filter
    # Bullish Trend: Price is above MA50 AND MA20 is above MA50
    is_trend_bullish = (close > ma50) and (ma20 > ma50)
    
    # 2. Setup Filter (Pullback)
    # RSI between 45 and 55
    is_pullback = (rsi >= 45) and (rsi <= 55)
    
    # 3. Volume Confirmation
    # Today's Volume > Average Volume 20
    is_volume_spike = (vol > vol_ma)
    
    # Decision Logic (Strict AND)
    is_valid_signal = is_trend_bullish and is_pullback and is_volume_spike
    
    reason = []
    if not is_trend_bullish: reason.append("Not Bullish Trend")
    if not is_pullback: reason.append("RSI Not in Zone (45-55)")
    if not is_volume_spike: reason.append("Low Volume")
    
    # Construct Buy Plan if Valid
    buy_area = f"{int(close)} - {int(close * 1.02)}"
    # Stop loss below recent support or 2*ATR
    stop_loss_price = int(close - (2 * atr)) 
    target_price = int(close + (3 * atr)) # 1.5R roughly
    
    risk_pct = round(((close - stop_loss_price) / close) * 100, 2)
    reward_pct = round(((target_price - close) / close) * 100, 2)

    return {
        "symbol": "", # To be filled by caller
        "date": str(curr.name.date()),
        "close": close,
        "ma20": ma20,
        "ma50": ma50,
        "rsi": rsi,
        "vol": vol,
        "vol_ma": vol_ma,
        "trend_status": "Bullish" if is_trend_bullish else "Bearish/Choppy",
        "setup_status": "Valid" if is_valid_signal else "Invalid",
        "buy_area": buy_area,
        "stop_loss": stop_loss_price,
        "target": target_price,
        "risk_pct": risk_pct,
        "reward_pct": reward_pct,
        "decision": "WATCHLIST" if is_valid_signal else "NO TRADE",
        "valid": is_valid_signal,
        "reason": ", ".join(reason) if reason else "Perfect Setup",
        # For Telegram Context
        "resistance": resistance,
        "support": support
    }
