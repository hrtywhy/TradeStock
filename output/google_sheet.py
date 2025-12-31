import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import sys
import os

# Add parent to path for config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def update_sheet(data_list):
    """
    Updates the Google Sheet with the latest scanning results.
    
    Args:
        data_list (list of dict): List of result dictionaries from strategy.
    
    Returns:
        bool: True if successful
    """
    if not data_list:
        print("No data to update to Google Sheet.")
        return False

    try:
        # Check if credentials exist
        if not os.path.exists(config.GOOGLE_SHEET_JSON_KEYFILE):
            print(f"Error: {config.GOOGLE_SHEET_JSON_KEYFILE} not found. Cannot update Sheet.")
            return False

        creds = Credentials.from_service_account_file(config.GOOGLE_SHEET_JSON_KEYFILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        
        # Open by ID
        sheet = client.open_by_key(config.GOOGLE_SHEET_ID).sheet1 # Assumes first sheet
        
        # Prepare DataFrame
        df = pd.DataFrame(data_list)
        
        # Select and Rename Columns to match requirements
        # Required: Date, Stock Code, Sector, Last Price, MA20, MA50, RSI, Vol, VolAvg, Trend, Setup, Buy, SL, TP, Risk, Reward, Decision
        
        # Map our keys to headers
        # Note: 'sector' might be missing if we didn't fetch it effectively. We'll handle that in main loop.
        


        # Curated Columns (Reduced) based on user feedback "Too much data"
        display_columns = [
            "date", "symbol", "decision", "reasons", "buy_area", "target", "news_summary"
        ]
        

        # Ensure all columns exist
        for col in display_columns:
            if col not in df.columns:
                df[col] = "-"
        
        # KEY FIX: Replace NaN/Inf with 0 or string to prevent JSON errors
        df_final = df[display_columns].fillna(0).replace([float('inf'), float('-inf')], 0)
        
        # Rename for Sheet Headers
        headers = [
            "Date", "Stock", "Decision", "Analysis (Short)", "Buy Zone", "Target", "AI Sentiment"
        ]
        
        # Prepare list of lists
        values = [headers] + df_final.values.tolist()
        
        # Clear and Update
        sheet.clear()
        sheet.update(range_name='A1', values=values)
        
        print("Google Sheet updated successfully.")
        return True

    except Exception as e:
        print(f"Error updating Google Sheet: {e}")
        return False
