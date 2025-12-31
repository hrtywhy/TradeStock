[![Live Market Scan Loop](https://github.com/hrtywhy/TradeStock/actions/workflows/daily_scan.yml/badge.svg)](https://github.com/hrtywhy/TradeStock/actions/workflows/daily_scan.yml)

# IDX Swing Trading System

A fully automated, real-time swing trading signal generator for the Indonesia Stock Exchange (IDX). This system monitors the market continuously during trading hours, identifying high-momentum swing setups and delivering instant alerts.

## Features

- **Live Market Monitoring**: 
  - Runs continuously from **08:00 to 16:00 WIB** (Western Indonesia Time).
  - Scans the market every minute to catch moves as they happen.
  - Automatically pauses during market close/weekends.

- **Dynamic Stock Universe**: 
  - Automatically fetches the entire list of IDX stocks (900+ tickers) via API.
  - No manual updating of stock lists required; automatically captures new IPOs.

- **Swing Strategy**: 
  - **Trend Filter**: Price above MA20 and MA50.
  - **Momentum**: RSI between 45 and 55 (Pullback zone) with recent crossover.
  - **Volume**: Volume breakout or consistent liquidity check.
  - **Sector Context**: (In Progress) Adds sector mapping for verification.

- **Real-Time Outputs**:
  - **Telegram Alerts**: Instant notification when a valid setup is confirmed. Smart filtering prevents duplicate alerts for the same stock in a single day.
  - **Google Sheet Dashboard**: Updates a centralized sheet with scan results for comprehensive review.

## Architecture

The system is designed to run 24/7 on **GitHub Actions** (Serverless):
- **Cron Jobs**: Triggers hourly sessions during market days.
- **Relay Loop**: Each session runs for 60 minutes, ensuring continuous coverage without server costs.
- **Timezone Aware**: Strictly operates on WIB (UTC+7) regardless of server location.

## Setup Instructions

### 1. Python Environment
Install the required libraries:
```bash
pip install -r requirements.txt
```

### 2. Google Sheets API Setup
1. Create a Project in [Google Cloud Console](https://console.cloud.google.com/) and enable **Google Sheets API**.
2. Create a **Service Account**, generate a JSON key, and save it as `tradestock-bot-7269f6a7604c.json`.
3. Share your target Google Sheet with the Service Account email.

### 3. Telegram Bot Setup
1. Create a new bot via [@BotFather](https://t.me/BotFather) to get your **API Token**.
2. Get your Chat ID.
3. Securely configure `config.py` or use environment variables for deployment.

## Usage

### Run Live Monitor (Local)
To start the bot in live mode (auto-sleeps when market is closed):
```bash
python main.py
```

### Run Single Scan
To process the entire market once and exit:
```bash
python main.py --run-now
```

## Configuration
- **Universe**: Managed dynamically by `data/stock_universe.py`.
- **Strategy Params**: adjustable in `config.py` (MA periods, RSI thresholds).
- **Secrets**: stored in `secrets/` folder (git-ignored) or GitHub Secrets for production.
