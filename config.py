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
        FINNHUB_API_KEY = api_creds.get('finnhub_api_key')
        POLYGON_API_KEY = api_creds.get('polygon_api_key')
        MARKETAUX_API_KEY = api_creds.get('marketaux_api_key')
        NEWSAPI_KEY = api_creds.get('newsapi_key')
        NEWSDATA_KEY = api_creds.get('newsdata_key')

    # Load Google Sheet Config
    with open(os.path.join(os.path.dirname(__file__), 'secrets', 'google_config.json'), 'r') as f:
        g_creds = json.load(f)
        GOOGLE_SHEET_ID = g_creds.get('sheet_id')
        GOOGLE_SHEET_JSON_KEYFILE = g_creds.get('json_keyfile')
        GOOGLE_SHEET_NAME = g_creds.get('sheet_name')
        
except Exception as e:
    print(f"Error loading secrets: {e}")
    TELEGRAM_BOT_TOKEN = None
    TELEGRAM_CHAT_ID = None
    GENAI_API_KEY = None
    GOOGLE_SHEET_ID = None
    GOOGLE_SHEET_JSON_KEYFILE = None
    FINNHUB_API_KEY = None
    POLYGON_API_KEY = None
    MARKETAUX_API_KEY = None
    NEWSAPI_KEY = None
    NEWSDATA_KEY = None

# Gemini AI API Key
# Loaded from secrets now.

# Telegram Configuration
# Loaded from secrets/telegram_creds.json


# Google Sheet Configuration
# Loaded from secrets/google_config.json

# Strategy Parameters
MA_FAST = 20
MA_SLOW = 50
RSI_PERIOD = 14
RSI_LOWER = 45
RSI_UPPER = 55
VOL_MA_PERIOD = 20
