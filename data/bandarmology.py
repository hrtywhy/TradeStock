
import random

class Bandarmology:
    def __init__(self):
        pass

    def get_net_foreign_flow(self, symbol):
        """
        Simulates fetching Net Foreign Buy/Sell.
        Returns: +Val (Inflow), -Val (Outflow)
        """
        # TODO: Implement actual scraping from 'http://idx.co.id' or 'ipot'.
        # For now, we return 0 or a mock value because real scraping 
        # requires complex auth/cookies manipulation that disrupts the flow if failed.
        return 0

    def calculate_flow_proxies(self, df):
        """
        Calculates proxies for Accumulation, Money Flow, and Circulation.
        
        Args:
           df (pd.DataFrame): Must contain 'High', 'Low', 'Close', 'Volume'.
           
        Returns:
           dict: {
               'accumulation_value': float, # Estimated Net Buy Value
               'money_flow_status': str,    # 'Positive' or 'Negative'
               'circulation_value': float,  # Total Transaction Value
               'passed_filters': bool
           }
        """
        if df is None or len(df) < 2:
            return None
            
        curr = df.iloc[-1]
        close = curr['Close']
        high = curr['High']
        low = curr['Low']
        vol = curr['Volume']
        
        # 3. Clean Money / Circulation: Total Value traded today
        circulation_value = vol * close
        
        # 2. Money Flow Proxy (MFM)
        # Multiplier = [(Close - Low) - (High - Close)] / (High - Low)
        # If High == Low, MFM = 0
        if high == low:
            mfm = 0
        else:
            mfm = ((close - low) - (high - close)) / (high - low)
            
        # 1. Big Accumulation Proxy
        # Net Flow Value = MFM * Circulation
        accumulation_value = mfm * circulation_value
        
        # Conditions
        # 1. Accum > 500,000,000
        # 2. MF > 0 (Implied if Accum > 500M, but we check explicitly)
        # 3. Circulation > 100,000,000
        
        passed = False
        reasons = []
        
        # Thresholds (IDR)
        TH_ACCUM = 500_000_000
        TH_CIRC = 100_000_000
        
        if accumulation_value > TH_ACCUM:
            if circulation_value > TH_CIRC:
                 # If Accum > 500M, it implies MF > 0 (since 500M is positive)
                 passed = True
            else:
                 reasons.append("Circulation < 100M")
        else:
             if accumulation_value <= 0:
                 reasons.append("Outflow/Distribution")
             else:
                 reasons.append(f"Accum {accumulation_value:,.0f} < 500M")
                 
        return {
            "accumulation_value": accumulation_value,
            "money_flow_status": "Positive" if accumulation_value > 0 else "Negative",
            "circulation_value": circulation_value,
            "passed_filters": passed,
            "reasons": reasons
        } 
