import schedule
import time
import pandas as pd
import datetime
import yfinance as yf
import sys

print("[DEBUG] Loading main.py v1.2 ...")

import config
from data.market_data import fetch_data, get_latest_news
from indicators.indicators import add_indicators
from strategy.swing_filter import check_swing_setup
from output.google_sheet import update_sheet
from output.telegram_alert import send_telegram_alert

def get_sector(symbol):
    try:
        t = yf.Ticker(symbol)
        return t.info.get('sector', 'Unknown')
    except:
        return 'Unknown'

# Track sent alerts to avoid spamming during live scan
SENT_ALERTS = set()
LAST_RESET_DATE = None

def get_wib_time():
    """Returns current time in WIB (UTC+7)"""
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    wib_tz = datetime.timezone(datetime.timedelta(hours=7))
    return utc_now.astimezone(wib_tz)

def is_market_open():
    """
    Checks if current time is within trading hours (08:00 - 16:00 WIB).
    """
    now = get_wib_time()
    
    # Check Weekday (Mon=0, Sun=6)
    if now.weekday() > 4:
        return False, "Weekend - Market Closed"
        
    current_time = now.time()
    market_start = datetime.time(8, 0)
    market_end = datetime.time(16, 0)
    
    if market_start <= current_time <= market_end:
        return True, "Market Open"
        
    return False, "Outside Trading Hours (08:00-16:00 WIB)"

def run_scan(live_mode=True):
    """
    Runs the scan logic.
    """
    scan_time = get_wib_time()
    print(f"\n[SCAN] Executing at {scan_time.strftime('%H:%M:%S')} (Live Mode: {live_mode})")
    
    results = []
    
    # 1. Iterate Universe
    for symbol in config.STOCK_UNIVERSE:
        # 2. Fetch Data
        df = fetch_data(symbol, period=config.HISTORY_PERIOD, interval=config.TIMEFRAME)
        if df is None:
            continue
            
        # 3. Add Indicators
        df = add_indicators(df)
        
        # 4. Strategy Check
        result = check_swing_setup(df)
        result['symbol'] = symbol
        result['sector'] = "IDX Stock"
        
        results.append(result)
        
        # 5. Telegram Alert
        if result['valid']:
             today_str = scan_time.strftime('%Y-%m-%d')
             alert_key = f"{symbol}_{today_str}"
             
             if live_mode and alert_key in SENT_ALERTS:
                 continue
                 
             print(f"!!! SIGNAL FOUND: {symbol} !!!")
             result['news'] = get_latest_news(symbol)
             send_telegram_alert(result)
             
             if live_mode:
                 SENT_ALERTS.add(alert_key)
    
    # 6. Update Google Sheet
    update_sheet(results)
    print(f"[COMPLETE] Processed {len(results)} stocks. Sheet updated.")

def start_bot(duration_minutes=None):
    global LAST_RESET_DATE
    print("--- IDX Swing Trading Bot Started ---")
    print("Schedule: Daily 08:00 - 16:00 WIB (Every 1 min)")
    if duration_minutes:
        print(f"Mode: One-time session for {duration_minutes} minutes.")
    
    start_time = datetime.datetime.now()
    
    while True:
        # Check duration limit (for GH Actions)
        if duration_minutes:
            elapsed = (datetime.datetime.now() - start_time).total_seconds() / 60
            if elapsed >= duration_minutes:
                print(f"[STOP] Duration limit of {duration_minutes}m reached. Exiting session.")
                break

        now = get_wib_time()
        
        # Daily Reset
        if LAST_RESET_DATE != now.date():
            print(f"[SYSTEM] New Day Detected ({now.date()}). Resetting alert cache.")
            SENT_ALERTS.clear()
            LAST_RESET_DATE = now.date()
            
        is_open, status = is_market_open()
        
        if is_open:
            try:
                run_scan(live_mode=True)
            except Exception as e:
                print(f"[ERROR] Scan failed: {e}")
            
            time.sleep(60)
            
        else:
            print(f"[WAITING] {status}. Time: {now.strftime('%H:%M:%S')}", end='\r')
            # If strictly limited duration and market is closed, we might just want to exit to save minutes?
            # But user logic says wait. For GH Actions, if market closed, we should probably exit immediately to save bill.
            if duration_minutes:
                 print("\n[STOP] Market is closed and duration limit is set. Exiting to save resources.")
                 break
            time.sleep(60)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-now", action="store_true", help="Run a single scan immediately")
    parser.add_argument("--live", action="store_true", help="Start live market monitoring (infinite loop)")
    parser.add_argument("--duration", type=int, help="Run live monitor for X minutes then exit (for Cron/CI)")
    args = parser.parse_args()

    try:
        if args.run_now:
            run_scan(live_mode=True)
        elif args.duration:
            start_bot(duration_minutes=args.duration)
        else:
            # Default to infinite live monitor if no args or --live
            start_bot()
            
    except KeyboardInterrupt:
        print("\n[STOP] Bot stopped by user.")
        sys.exit(0)
