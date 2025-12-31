
# 📈 IDX Swing Trading System

A sophisticated automated trading system for the Indonesia Stock Exchange (IDX) that uses a **Multi-Analyst "Council" Strategy** to filter high-probability swing trading setups.

## 🚀 Features

*   **Council of Analysts Strategy**:
    *   **🔧 Technical Analyst**: Validates Trend (MA20/50), RSI Pullbacks, and Volume.
    *   **📊 Fundamental Analyst**: Filters by Market Cap (>1T), ROE (>5%), and PE Ratio (<15).
    *   **🌊 Flow Analyst**: Detects "Bandar" accumulation via Volume Spikes (Proxy) or Broker Summary (Plugin ready).
    *   **🤖 Sentiment Analyst**: Uses **Google Gemini AI** to scan news and reject trades with negative sentiment (Bankruptcy, Corruption).
*   **Confluence Scoring**: Setups are scored (0-100). Only scores > 70 are actionable.
*   **Automated Alerts**: Sends beautiful Telegram alerts with Trade Plans and AI summaries.
*   **Dashboard**: Auto-updates a Google Sheet with scan results.

## 📂 Project Structure

```

├── config.py               # Configuration (Universe, Timeframe, API Keys)
├── main.py                 # Main entry point (Scan Loop)
├── data/
│   ├── market_data.py      # OHLCV Fetcher (yfinance)
│   ├── bandarmology.py     # Flow Analysis / Broker Summary
│   ├── stock_universe.py   # Dynamic Stock List
│   └── idx_universe_cache.json
├── indicators/
│   ├── indicators.py       # TA Library (RSI, MA, ATR)
│   └── sentiment.py        # AI News Analysis
├── strategy/
│   ├── score_strategy.py   # Main Council Logic (Confluence)
│   └── fundamental_analyst.py # Fundamental Filters
├── output/
│   ├── telegram_alert.py   # Bot Notifier
│   └── google_sheet.py     # Dashboard Updater

```


## 🛠️ Setup

1.  **Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Configuration**:

    *   **Secrets**:
        *   Create `secrets/api_keys.json`: `{"api_key": "YOUR_GEMINI_KEY"}`
        *   Create `secrets/telegram_creds.json`: `{"bot_token": "...", "chat_id": "..."}`
        *   Create `secrets/google_config.json`: `{"sheet_id": "...", "json_keyfile": "...", "sheet_name": "..."}`
    *   **Google Sheet**: Place `tradestock-bot-....json` in root (GitIgnored).
    ```bash
    # Run a single immediate scan
    python main.py --run-now

    # Run Live Monitor (08:00-16:00 WIB)
    python main.py --live
    ```

## 🧠 Strategy Logic (The Council)

| Analyst | Weight | Criteria |
| :--- | :--- | :--- |

| **Technical** | 40 pts | Bullish Trend (MA20>MA50), RSI 40-60, Vol > Avg |
| **Fundamental** | 20 pts | Market Cap > 1T, ROE > 5% |
| **Flow** | 20 pts | Price Up + Vol Spike (Smart Money Proxy) |
| **AI Sentiment**| 20 pts | **Deep Research**: Scans Official IDX Disclosures & News. Penalty for Bad News. |

**Thresholds:**
*   **WATCHLIST**: Score > 70
*   **STRONG BUY**: Score > 80

## ⚠️ Disclaimer
Trading stocks involves risk. This tool provides analysis, not financial advice. "Do your best, let God do the rest."
