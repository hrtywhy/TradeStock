import yfinance as yf

def check_idx_components():
    try:
        idx = yf.Ticker("^JKSE")
        print("IHSG Components (via yfinance):??")
        # Some versions/indices support this
        # print(idx.tickers) 
        # print(idx.components)
        print("Done")
    except Exception as e:
        print(e)
        
if __name__ == "__main__":
    check_idx_components()
