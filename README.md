[![IDX Swing Trade Scan](https://github.com/hrtywhy/TradeStock/actions/workflows/daily_scan.yml/badge.svg)](https://github.com/hrtywhy/TradeStock/actions/workflows/daily_scan.yml)

# IDX Swing Trading System

A fully automated swing trading watchlist and signal generator for the specific Indonesia Stock Exchange (IDX) stocks.

## Features
- **Daily Scan**: Runs automatically at 08:00 WIB.
- **Strategy**: Trend Following + Pullback (RSI 45-55) + Volume Confirmation.
- **Outputs**:
  - Auto-updating to Google Sheet as a Daily Notes Stock Watchlist.
  - Telegram Alerts.

## Setup Instructions

### 1. Python Environment
Install the required libraries:
```bash
pip install -r requirements.txt
```

### 2. Google Sheets API Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a Project and enable **Google Sheets API** and **Google Drive API**.
3. Create a **Service Account**, generate a JSON key, and download it.
4. Rename the file to `credentials.json`.
5. Share your Google Sheet with the `client_email` found inside `credentials.json` (Give Editor access).

### 3. Telegram Bot Setup
1. Chat with [@BotFather](https://t.me/BotFather) on Telegram.
2. Create a new bot (`/newbot`) to get your **API Token**.
3. Get your Chat ID.
4. Open `config.py` and update:
   ```python
   TELEGRAM_BOT_TOKEN = "YOUR_TOKEN"
   TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"
   ```

## Usage

### Run Manually
To run the scan immediately (for testing):
```bash
python main.py --run-now
```

### Run Scheduler
To start the daily scheduler (runs at 08:00 WIB):
```bash
python main.py
```
Keep the terminal open or run it on a VPS/Server.

## Configuration
Modify `config.py` to:
- Add/Remove stocks in `STOCK_UNIVERSE`.
- Change indicator parameters (MA periods, RSI levels).
