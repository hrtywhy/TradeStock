
import pandas as pd
from indicators.sentiment import get_market_sentiment
from data.bandarmology import Bandarmology
from strategy.fundamental_analyst import FundamentalAnalyst

class ConfluenceStrategy:
    def __init__(self):
        self.bandarmology = Bandarmology()
        self.fundamentals = FundamentalAnalyst()

    def calculate_score(self, df, symbol):
        """
        Calculates a 'Council of Analysts' Score (0-100).
        Strict Logic: Must pass Technicals to even check Fundamentals/AI.
        """
        if df is None or len(df) < 50:
            return {
                "valid": False, "score": 0, "decision": "NO DATA", "symbol": symbol
            }

        curr = df.iloc[-1]
        score = 0
        analyst_notes = {
            "Technical": [],
            "Fundamental": [],
            "Sentiment": [],
            "Flow": []
        }

        # --- 1. Technical Analyst (Max 40 pts) ---
        # PRIMARY FILTER: If Trend is Bearish, we STOP immediately (unless oversold bounce strategy, but user wants restrict).
        
        tech_score = 0
        close = curr['Close']
        ma20 = curr['MA20']
        ma50 = curr['MA50']
        rsi = curr['RSI']
        vol = curr['Volume']
        vol_ma = curr['VolMA20']
        
        # Trend
        if ma20 > ma50:
            tech_score += 15
            analyst_notes["Technical"].append("Bullish Trend")
        elif close > ma50:
            tech_score += 5
            analyst_notes["Technical"].append("Price > MA50")
        else:
            # STRICT FILTER: If Price < MA50, Ignore entirely.
            if not (rsi < 30): # Unless extremely oversold
                 return {"valid": False, "score": 0, "decision": "BEARISH_SKIP", "symbol": symbol}

        # RSI
        if 50 <= rsi <= 60:
            tech_score += 15
            analyst_notes["Technical"].append("Strong Momentum Zone")
        elif 40 <= rsi <= 50:
            tech_score += 10
            analyst_notes["Technical"].append("Pullback Zone")
            
        # Volume
        if vol > vol_ma:
            tech_score += 10
            analyst_notes["Technical"].append("Vol > Avg")

        score += tech_score

        # If Technical score is too low (< 20), don't waste API calls on others
        if score < 20:
             return {"valid": False, "score": score, "decision": "WEAK_TECH", "symbol": symbol}

        # --- 2. Fundamental Analyst (Max 20 pts) ---
        fund_score, fund_reasons = self.fundamentals.analyze(symbol)
        analyst_notes["Fundamental"] = fund_reasons
        score += fund_score

        # --- 3. Flow Analyst (Net Foreign/Bandar) (Max 20 pts) ---
        # The User specified "Net Foreign Buy" is priority. 
        # Since we don't have real scraper, we use Volume Flow proxy AND Bandarmology structure.
        flow_score = 0
        
        # Proxy: If Price Up AND Volume Up significantly
        if close > df.iloc[-2]['Close'] and vol > (vol_ma * 1.5):
            flow_score += 10
            analyst_notes["Flow"].append("Strong Inflow Est.")
            
        # Bandarmology Placeholder (If configured)
        b_score = self.bandarmology.get_broker_summary(symbol)
        if b_score and b_score > 1.0:
            flow_score += 10
            analyst_notes["Flow"].append("Broker Accumulation")
            
        score += flow_score

        # --- 4. Sentiment/News Analyst (Max 20 pts) ---
        # Only fetch if we are looking good (Score > 50 so far)
        if score >= 50:
            ai_score, ai_reason = get_market_sentiment(symbol)
            if ai_score > 20:
                score += 20
                analyst_notes["Sentiment"].append("Positive News")
            elif ai_score < -20:
                score -= 20 # PENALTY
                analyst_notes["Sentiment"].append("Negative News")
            else:
                 analyst_notes["Sentiment"].append("Neutral News")
            
            analyst_notes["Sentiment"].append(f"AI: {ai_reason}")


        # --- Final Decision & Formatting ---
        # Threshold: Increased to 70 for Watchlist
        decision = "NO TRADE"
        valid = False
        
        if score >= 80:
            decision = "STRONG BUY"
            valid = True
        elif score >= 60:
            decision = "WATCHLIST"
            valid = True
            
        # Collect all raw notes for Status Line
        flat_notes = []
        for notes in analyst_notes.values():
            flat_notes.extend(notes)
            
        # Limit status line length (top 3-4 reasons)
        status_line = ", ".join(flat_notes[:4]) 

        return {
            "symbol": symbol,
            "date": str(curr.name.date()),
            "score": score,
            "decision": decision,
            "valid": valid,
            "reasons": status_line, # Used for Status line
            
            "close": close,
            "rsi": rsi,
            "trend_status": "Bullish" if ma20 > ma50 else "Bearish",
            "vol_ma": vol_ma,
            "vol": vol,
            "buy_area": f"{int(close)} - {int(close * 1.02)}",
            "stop_loss": int(close * 0.95),
            "target": int(close * 1.05),
            "risk_pct": 5.0,
            "reward_pct": 5.0,
            "news_summary": "; ".join(analyst_notes["Sentiment"])
        }
