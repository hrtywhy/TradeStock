
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

        # --- 1. Technical Analyst (Max 30 pts) ---
        tech_score = 0
        close = curr['Close']
        ma20 = curr['MA20']
        ma50 = curr['MA50']
        rsi = curr['RSI']
        vol = curr['Volume']
        vol_ma = curr['VolMA20']

        # --- 2. Flow Analyst (Net Foreign/Bandar) (Max 45 pts) ---
        # Moved UP to prioritize Bandarmology as per User preference
        flow_score = 0
        has_strong_flow = False
        
        # Proxy: If Price Up AND Volume Up significantly (Smart Money Proxy)
        if close > df.iloc[-2]['Close'] and vol > (vol_ma * 1.5):
            flow_score += 10
            has_strong_flow = True
            analyst_notes["Flow"].append("Smart Money Proxy (Vol Spike)")
            
        # --- Bandarmology Filter Engine (Hard Filter) ---
        flow_data = self.bandarmology.calculate_flow_proxies(df)
        
        passed_flow = False
        if flow_data and flow_data['passed_filters']:
             passed_flow = True
             flow_score += 15
             has_strong_flow = True
             
             # Check for Massive Foreign/Smart Money Flow
             accum_val = flow_data['accumulation_value']
             if accum_val >= 50_000_000_000: # > 50B
                  analyst_notes["Flow"].append("Whale Accumulation (>50B)")
                  flow_score += 20 # Huge Bonus
             elif accum_val >= 5_000_000_000: # > 5B
                  analyst_notes["Flow"].append("Major Foreign Buy (>5B)")
                  flow_score += 10 # Bonus
             else:
                  analyst_notes["Flow"].append(f"Big Accum (>500M)")
                  
             analyst_notes["Flow"].append(f"Circulation {flow_data['circulation_value']/1_000_000:.0f}M")

        score += flow_score

        # --- 3. Technical Analyst (Max 30 pts) ---
        tech_score = 0
        close = curr['Close']
        ma20 = curr['MA20']
        ma50 = curr['MA50']
        rsi = curr['RSI']
        vol = curr['Volume']
        vol_ma = curr['VolMA20']
        
        # Trend
        if ma20 > ma50:
            tech_score += 10
            analyst_notes["Technical"].append("Bullish Trend")
        elif close > ma50:
            tech_score += 5
            analyst_notes["Technical"].append("Price > MA50")
        else:
            # STRICT FILTER: If Price < MA50, Ignore entirely.
            if not (rsi < 30): 
                 return {
                     "valid": False,
                     "score": 0,
                     "decision": "BEARISH_SKIP",
                     "reasons": "Trend Bearish (< MA50)",
                     "symbol": symbol
                 }

        # RSI - Adjusted for Momentum
        if 50 <= rsi <= 75:
            tech_score += 10
            analyst_notes["Technical"].append("Strong Momentum")
        elif 40 <= rsi < 50:
            tech_score += 5
            analyst_notes["Technical"].append("Pullback Zone")
        elif rsi > 75:
            tech_score += 5 # Warning but still points
            analyst_notes["Technical"].append("Overbought (>75)")
            
        # Volume
        if vol > vol_ma:
            tech_score += 10
            analyst_notes["Technical"].append("Vol > Avg")

        score += tech_score

        # Cutoff: If Tech < 20 AND Flow is Weak, Skip.
        # But if Flow is Strong (passed_flow), we allow it even if Tech is mediocre.
        if tech_score < 15 and not passed_flow:
             return {"valid": False, "score": score, "decision": "WEAK_TECH", "symbol": symbol}
        
        # --- 4. Fundamental Analyst (Max 15 pts) ---
        fund_score, fund_reasons = self.fundamentals.analyze(symbol)
        analyst_notes["Fundamental"] = fund_reasons
        score += fund_score

        # --- 5. Sentiment/News Analyst (Max 20 pts) ---
        # Only fetch if we are looking good (Score > 45)
        if score >= 45:
            ai_score, ai_reason = get_market_sentiment(symbol)
            
            sentiment_label = "Neutral News"
            if ai_score > 20:
                score += 20
                sentiment_label = "Positive News based on AI"
            elif ai_score < -20:
                score -= 20 # PENALTY
                sentiment_label = "Negative News based on AI"
            
            analyst_notes["Sentiment"].append(sentiment_label)
            analyst_notes["Sentiment"].append(ai_reason)


        # --- Final Decision & Formatting ---
        # Threshold: Increased to 70 for Watchlist
        # CRITICAL: STRONG BUY requires Strong Flow (Foreign Buy / Bandar)
        decision = "NO TRADE"
        valid = False
        
        if score >= 85 and has_strong_flow:
            decision = "STRONG BUY"
            valid = True
        elif score >= 65:
            decision = "WATCHLIST"
            valid = True
        elif flow_score >= 30:
            decision = "BIG ACCUM FOCUS"
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
            "news_summary": "\n".join(analyst_notes["Sentiment"])
        }
