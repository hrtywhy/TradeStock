
import yfinance as yf
import pandas as pd

class FundamentalAnalyst:
    def __init__(self):
        self.cache = {}

    def analyze(self, symbol):
        """
        Returns a score (0-20) and a reason.
        Checks:
        1. Market Cap (Avoid micro-caps, > 1T IDR)
        2. PE Ratio (0 < PE < 40)
        3. ROE (> 5%)
        """
        try:
            # Check cache to avoid spamming yfinance if we re-scan
            # In a live loop, we might want to refresh this daily.
            if symbol in self.cache:
                return self.cache[symbol]

            t = yf.Ticker(symbol)
            info = t.info
            
            score = 0
            reasons = []
            
            # 1. Market Cap (> 500 Billion IDR) - Filter 'Gorengan' lightly
            mcap = info.get('marketCap', 0)
            if mcap is None: mcap = 0
            
            if mcap > 10_000_000_000_000: # > 10T (Blue Chip)
                score += 7
                reasons.append("Blue Chip")
            elif mcap > 1_000_000_000_000: # > 1T (Mid Cap)
                score += 4
                reasons.append("Mid Cap")
            else:
                reasons.append("Micro Cap (High Risk)")
                
            # 2. Profitability (ROE)
            roe = info.get('returnOnEquity', 0)
            if roe is None: roe = 0
            if roe > 0.15: # > 15%
                score += 4
                reasons.append("High ROE")
            elif roe > 0.05:
                score += 2
                reasons.append("Profitable")
                
            # 3. Valuation (PE)
            pe = info.get('trailingPE', 0)
            if pe is None: pe = 0
            
            if 0 < pe < 15:
                score += 4
                reasons.append("Undervalued (PE<15)")
            elif 0 < pe < 30:
                score += 2
                reasons.append("Fair Value")
            elif pe > 50:
                score -= 5 # Penalty remains
                reasons.append("Overvalued")

            result = (score, reasons)
            self.cache[symbol] = result
            return result
        except Exception as e:
            print(f"[WARN] Fundamental Check Failed for {symbol}: {e}")
            return 0, ["N/A"]
