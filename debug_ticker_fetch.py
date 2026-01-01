from webull_client import WebullClient
import json

print("--- DEBUG TIER FAILING ---")
client = WebullClient()

if client.is_logged_in:
    print("Login State: LOGGED IN")
else:
    print("Login State: NOT LOGGED IN (Critical)")

symbol = "SPY"
print(f"\n1. Calling get_ticker('{symbol}')...")
try:
    # Access internal wb directly to see raw return
    raw = client.wb.get_ticker(symbol)
    print(f"Raw Result Type: {type(raw)}")
    print(f"Raw Result: {raw}")
except Exception as e:
    print(f"get_ticker FAILED: {e}")

print(f"\n2. Calling client.get_ticker_id('{symbol}')...")
tid = client.get_ticker_id(symbol)
print(f"Resolved TID: {tid}")

if tid:
    print(f"\n3. Calling get_options_expiration_dates({tid})...")
    try:
        dates = client.wb.get_options_expiration_dates(tid)
        print(f"Dates: {dates}")
    except Exception as e:
        print(f"get_options_expiration_dates FAILED: {e}")
        import traceback
        traceback.print_exc()

print("\n--------------------------")
