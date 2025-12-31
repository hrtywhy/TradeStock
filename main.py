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

def run_daily_scan():
    print(f"\n[SCAN START] Running Daily Swing Scan v1.1 at {datetime.datetime.now()}")
    
    results = []
    
    # 1. Iterate Universe
    for symbol in config.STOCK_UNIVERSE:
        # print(f"Processing {symbol}...", end='\r')
        
        # 2. Fetch Data
        df = fetch_data(symbol, period=config.HISTORY_PERIOD, interval=config.TIMEFRAME)
        if df is None:
            continue
            
        # 3. Add Indicators
        df = add_indicators(df)
        
        # 4. Strategy Check
        result = check_swing_setup(df)
        result['symbol'] = symbol
        
        # Fetch Sector (Slows down? Let's check. If too slow, removing)
        # result['sector'] = get_sector(symbol) # Commented out for speed, usually static mapping is better
        result['sector'] = "IDX Stock" 
        
        results.append(result)
        
        # 5. Telegram Alert (Immediate or Batch?)
        # Requirement: "Send Telegram messages ONLY when all swing criteria are met"
        if result['valid']:
             print(f"!!! SIGNAL FOUND: {symbol} !!!")
             # Fetch news for context
             result['news'] = get_latest_news(symbol)
             send_telegram_alert(result)
    
    # 6. Update Google Sheet (All results, including non-signals, for full view?)
    # "The system should produce: Fully automated daily swing watchlist"
    # Usually a watchlist contains CANDIDATES. 
    # But the sheet requirements ask for "Decision (WATCHLIST / NO TRADE)". 
    # So we upload ALL.
    print(f"\n[SCAN COMPLETE] Processed {len(results)} stocks.")
    update_sheet(results)
    print("[Update] Google Sheet updated.")

def job():
    run_daily_scan()

if __name__ == "__main__":
    print("--- IDX Swing Trading System Initialized ---")
    print(f"Targeting: {len(config.STOCK_UNIVERSE)} stocks.")
    print("Scheduled for 08:00 WIB Daily.")
    
    # Schedule
    # WIB is UTC+7. If server is UTC, 08:00 WIB is 01:00 UTC.
    # Need to handle timezone checks. For now, assuming local system time.
    schedule.every().day.at("08:00").do(job)
    
    # Provide a CLI menu
    print("1. Run Scan NOW")
    print("2. Start Scheduler Loop")
    
    # Simple input check (blocking) or typically just run scheduler
    # For this interactive enviroment, I will set it to run scheduler but also valid to run once.
    
    # Argument parser to run once?
    # Argument parser to run once
    if len(sys.argv) > 1 and sys.argv[1] == "--run-now":
        run_daily_scan()
        sys.exit(0)

    while True:
        schedule.run_pending()
        time.sleep(60)
