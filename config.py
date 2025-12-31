# Configuration for ID Swing Trading System

# List of stocks to scan (IDX)
# Easy to modify/add new stocks here
from data.stock_universe import fetch_idx_universe

# List of stocks to scan (IDX)
# Dynamically fetched from external source to cover all IPOs/Tickers
try:
    STOCK_UNIVERSE = fetch_idx_universe()
    if not STOCK_UNIVERSE:
        raise Exception("Empty universe returned")
except Exception as e:
    print(f"[CONFIG] Warning: Failed to fetch dynamic universe ({e}). Using fallback list.")
    STOCK_UNIVERSE = [
        "UNTR.JK", "ASII.JK", "BBNI.JK", "TLKM.JK", "PGAS.JK", 
        "INCO.JK", "MDKA.JK", "HUMI.JK", "BRMS.JK", "ADRO.JK", 
        "ADMR.JK", "NICL.JK", "RAJA.JK", "RATU.JK", "ENRG.JK", 
        "DSSA.JK", "BBCA.JK", "BBRI.JK", "BMRI.JK", "GOTO.JK",
        "AMMN.JK", "MEDC.JK", "PTBA.JK", "UNVR.JK", "ICBP.JK"
    ]

# Timeframe Settings
TIMEFRAME = "1d"  # Daily
HISTORY_PERIOD = "1y" # Fetch 1 year of data to ensure enough for MA50 and MA200

import json
import os


# Load Secrets
try:
    with open(os.path.join(os.path.dirname(__file__), 'secrets', 'telegram_creds.json'), 'r') as f:
        creds = json.load(f)
        TELEGRAM_BOT_TOKEN = creds.get('bot_token')
        TELEGRAM_CHAT_ID = creds.get('chat_id')
        
    # Load Gemini Key
    with open(os.path.join(os.path.dirname(__file__), 'secrets', 'api_keys.json'), 'r') as f:
        api_creds = json.load(f)
        GENAI_API_KEY = api_creds.get('api_key')
        
except Exception as e:
    print(f"Error loading secrets: {e}")
    TELEGRAM_BOT_TOKEN = None
    TELEGRAM_CHAT_ID = None
    GENAI_API_KEY = None

# Gemini AI API Key
# Loaded from secrets now.

# Telegram Configuration
# Loaded from secrets/telegram_creds.json

# Google Sheet Configuration
GOOGLE_SHEET_JSON_KEYFILE = "tradestock-bot-7269f6a7604c.json" # Place your service account json in the root folder
GOOGLE_SHEET_NAME = "Swing Trading Watchlist" # The name of the sheet file typically, but we used ID in the prompt. 
# Better to use ID if possible, but gspread often uses name or open_by_url.
GOOGLE_SHEET_ID = "1hElfiC3HV7T2hbh28xDPXd7wRkz8HmBgB28QLSZcQhs"

# Strategy Parameters
MA_FAST = 20
MA_SLOW = 50
RSI_PERIOD = 14
RSI_LOWER = 45
RSI_UPPER = 55
VOL_MA_PERIOD = 20
