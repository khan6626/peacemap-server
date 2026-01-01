from webull_client import WebullClient
import pandas as pd
import traceback

print("--- DEBUG PROFILE FETCH WRAPPER ONLY ---")
# The previous debug script called client.wb.get_options(stock=tid) manually, which crashes.
# We want to test client.get_option_chain which SHOULD NOW USE SYMBOL.

client = WebullClient()
symbol = "SPY"
date = "2025-12-30" 

print(f"Logged In: {client.is_logged_in}")

try:
    dates = client.get_dates(symbol)
    if dates:
        target_date = dates[0]
        print(f"Using target date: {target_date}")
        
        print("\nTesting wrapper get_option_chain...")
        calls, puts = client.get_option_chain(symbol, target_date)
        
        if calls is not None:
            print(f"Calls DF shape: {calls.shape}")
            print(f"Puts DF shape: {puts.shape}")
            print("Head:")
            print(calls.head())
        else:
            print("get_option_chain returned None")
    else:
        print("No dates found.")
except Exception as e:
    print("CRASHED:")
    traceback.print_exc()

print("\n--- END DEBUG ---")
