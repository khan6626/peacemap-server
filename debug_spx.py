from webull_client import WebullClient
import json

print("--- DEBUGGING SPX DATES ---")
client = WebullClient()

if not client.is_logged_in:
    print("ERROR: Client NOT logged in. Attempting to load session explicitely...")
    client._load_session()

if not client.is_logged_in:
    print("FATAL: Still not logged in. Cannot fetch Webull data.")
else:
    print("Logged in successfully.")
    
    symbol = 'SPX'
    print(f"Fetching Ticker ID for {symbol}...")
    tid = client.get_ticker_id(symbol)
    print(f"Ticker ID: {tid} (Type: {type(tid)})")
    
    if tid:
        try:
            print(f"Fetching Dates for ID {tid}...")
            dates = client.get_dates(symbol)
            print(f"Dates found: {dates}")
        except Exception as e:
            print(f"Error fetching dates: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("Failed to get Ticker ID.")
