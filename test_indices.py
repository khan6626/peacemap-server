import yfinance as yf

def check_ticker(symbol, name):
    print(f"Checking {name} ({symbol})...")
    try:
        ticker = yf.Ticker(symbol)
        options = ticker.options
        if options:
            print(f"  SUCCESS: Found {len(options)} expiration dates.")
            print(f"  First date: {options[0]}")
            # Try fetching the chain for the first date
            chain = ticker.option_chain(options[0])
            print(f"  Calls: {len(chain.calls)}, Puts: {len(chain.puts)}")
        else:
            print("  FAILURE: No options dates found.")
    except Exception as e:
        print(f"  ERROR: {e}")
    print("-" * 20)

check_ticker('^GSPC', 'SPX')
check_ticker('^NDX', 'NDX')
check_ticker('IWM', 'IWM')
