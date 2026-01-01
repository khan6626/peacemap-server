from webull_client import WebullClient
import pandas as pd
import traceback

print("--- DEBUG PROFILE FETCH ---")
client = WebullClient()
symbol = "SPY"
date = "2025-12-30" # Ensure this date exists or use logic to get first date

print(f"Logged In: {client.is_logged_in}")

# 1. Test get_ticker_id
print("\n1. Testing get_ticker_id...")
tid = client.get_ticker_id(symbol)
print(f"TID: {tid}")

if tid:
    # 2. Test get_options
    print(f"\n2. Testing get_options(stock={tid}, expireDate={date})...")
    try:
        # We need to ensure date is valid. Fetch dates first.
        dates = client.get_dates(symbol)
        print(f"Available Dates: {dates[:3]}")
        if dates:
            target_date = dates[0]
            print(f"Using target date: {target_date}")
            
            opts = client.wb.get_options(stock=tid, expireDate=target_date)
            print(f"Raw Options Options Count: {len(opts)}")
            if len(opts) > 0:
                print(f"Sample Opt: {opts[0]}")
                
            # 3. Test wrapper get_option_chain
            print("\n3. Testing wrapper get_option_chain...")
            calls, puts = client.get_option_chain(symbol, target_date)
            print(f"Calls DF shape: {calls.shape}")
            print(f"Puts DF shape: {puts.shape}")
            print("Head:")
            print(calls.head())
        else:
            print("No dates found to test options.")
    except Exception as e:
        print("CRASHED:")
        traceback.print_exc()

print("\n--- END DEBUG ---")
