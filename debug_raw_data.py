from webull_client import WebullClient
import json

print("--- DEBUG RAW DATA ---")
client = WebullClient()
symbol = "SPY"

dates = client.get_dates(symbol)
if not dates:
    print("No dates found.")
    exit()

target_date = dates[0]
print(f"Target Date: {target_date}")

# Fetch raw options
# We use the symbol string as fixed previously
try:
    print("Fetching raw options...")
    raw_opts = client.wb.get_options(stock=symbol, expireDate=target_date)
    print(f"Total raw items: {len(raw_opts)}")
    
    if len(raw_opts) > 0:
        # Check unique directions
        directions = set()
        for o in raw_opts:
            directions.add(o.get('direction'))
        print(f"Unique directions found: {directions}")
        
        # Dump the first 2 items to file for inspection
        with open('raw_options_sample.json', 'w') as f:
            json.dump(raw_opts[:5], f, indent=2)
        print("Saved first 5 items to raw_options_sample.json")
    else:
        print("No options returned.")

except Exception as e:
    print(f"Error: {e}")
