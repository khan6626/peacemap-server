from webull_client import WebullClient

print("--- TESTING FIX ---")
client = WebullClient()
symbol = "SPY"

print(f"\nAttempt 1: Passing SYMBOL '{symbol}' to get_options_expiration_dates...")
try:
    dates = client.wb.get_options_expiration_dates(symbol)
    print(f"SUCCESS! Dates: {len(dates)} found.")
    print(dates[:3])
except Exception as e:
    print(f"FAILED with Symbol: {e}")

print(f"\nAttempt 2: Passing ID to get_options_expiration_dates (Previous method)...")
tid = client.get_ticker_id(symbol)
try:
    dates = client.wb.get_options_expiration_dates(tid)
    print(f"SUCCESS! Dates: {len(dates)} found.")
except Exception as e:
    print(f"FAILED with ID: {e}")

print("\n--- TESTING get_options ---")
if tid:
     # try with ID
     try:
         print("Try get_options with ID...")
         # Just verify it doesn't crash on invalid arg
         # client.wb.get_options(stock=tid) # requires expireDate
         pass
     except:
         pass
