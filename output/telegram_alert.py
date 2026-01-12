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
    message = f"""🔥POTENTIAL TICKER DETECTED🔥

Stock   : ${signal_data['symbol'].replace('.JK', '')} ({company_name})
Score   : {signal_data['score']}/100 
Decision: {signal_data['decision']}
Status : {signal_data['reasons']}

📌 Details:
• Trend  : {signal_data['trend_status']}
• RSI    : {signal_data['rsi']:.1f}
• Volume : {signal_data['vol']:,.0f} (Avg: {signal_data['vol_ma']:,.0f})

🎯 Plan  : 
• Buy    : {signal_data['buy_area']}
• Stop   : {signal_data['stop_loss']}
• Target : {signal_data['target']}
• Risk   : {signal_data['risk_pct']}%  
• Reward : {signal_data['reward_pct']}%

🤖 Sentiment Analysis:
{signal_data.get('news_summary', 'No News Found')}

⚠️ Risk Note
Always manage risk. 
Do your best let god do the rest

⏰ {current_time}
"""

    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "text": message
    }
    
    try:
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print(f"Failed to send Telegram alert: {response.text}")
        else:
            print(f"Telegram alert sent for {signal_data['symbol']}")
    except Exception as e:
        print(f"Error sending Telegram: {e}")
