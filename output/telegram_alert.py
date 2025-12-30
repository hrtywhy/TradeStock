import requests
import sys
import os
import yfinance as yf
from datetime import datetime

# Add parent to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def get_company_name(symbol):
    try:
        t = yf.Ticker(symbol)
        return t.info.get('longName', symbol)
    except:
        return symbol

def send_telegram_alert(signal_data):
    """
    Sends a Telegram alert for a valid swing setup.
    
    Args:
        signal_data (dict): Result dictionary from strategy.
    """
    if not signal_data.get("valid"):
        return

    company_name = get_company_name(signal_data['symbol'])
    current_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    
    # Construct Message
    # EXACT STRUCTURE from requirements
    message = f"""📈 SWING SETUP DETECTED (IDX)

Stock  	: ${signal_data['symbol'].replace('.JK', '')} ({company_name})
Status	: Breakout/Pullback Setup
Action	: BUY ON IMPLIED MOMENTUM
Trend  	: {signal_data['trend_status']}
RSI    	: {signal_data['rsi']:.1f} (Pullback Zone)
Vol    	: Above Avg 20D

📌 BUY AREA : {signal_data['buy_area']}

🛑 STOP LOSS : {signal_data['stop_loss']}

🎯 TARGET : {signal_data['target']}
• Risk: {signal_data['risk_pct']}% 
• Reward: {signal_data['reward_pct']}%

🎯 KEY CATALYST :
{signal_data.get('news', 'No recent news found.')}

⚠️ NOTES :
Pullback within uptrend, volume confirmation present.
Strictly check bid/offer before entry.

⚠️ RISK NOTE: 
Always manage risk. Volatility is expected.

⏰ TIME :
{current_time}
"""

    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML" # Or Markdown, but plain text is safer if symbols are weird. Sticking to plain text implicitly or HTML? 
        # The sample had bolding. Let's try to add no parse_mode first to be safe, or just standard text.
        # Actually user prompt used some bolding logic in visual representation, but raw text in python string.
        # I will send as plain text to ensure delivery, or minimal markdown.
    }
    
    try:
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print(f"Failed to send Telegram alert: {response.text}")
        else:
            print(f"Telegram alert sent for {signal_data['symbol']}")
    except Exception as e:
        print(f"Error sending Telegram: {e}")
