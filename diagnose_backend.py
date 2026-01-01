from webull_client import WebullClient
import json
import os

print("=== DIAGNOSTIC START ===")

# Check session file
if os.path.exists('webull_session.json'):
    print("[PASS] webull_session.json exists.")
    try:
        with open('webull_session.json', 'r') as f:
            data = json.load(f)
            print(f"      Token length: {len(data.get('access_token', ''))}")
            print(f"      Refresh Token length: {len(data.get('refresh_token', ''))}")
    except Exception as e:
        print(f"[FAIL] Error reading session file: {e}")
else:
    print("[FAIL] webull_session.json DOES NOT EXIST.")

# Initialize Client
client = WebullClient()
print(f"Client Logged In Status: {client.is_logged_in}")

# Try Fetching Ticker ID
for sym in ['SPX', 'TSLA', 'AAPL']:
    print(f"\n--- Testing {sym} ---")
    tid = client.get_ticker_id(sym)
    print(f"Ticker ID: {tid}")
    
    if tid:
        dates = client.get_dates(sym)
        print(f"Dates Found: {len(dates)}")
        if len(dates) > 0:
            print(f"First Date: {dates[0]}")
    else:
        print("Failed to resolve Ticker ID")

print("\n=== DIAGNOSTIC END ===")
