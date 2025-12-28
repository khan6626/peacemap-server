import requests
from datetime import datetime

print("Testing Barchart Connectivity from current location...")

url = "https://www.barchart.com/proxies/core-api/v1/options/get"

# Barchart requires specific headers and cookies usually.
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://www.barchart.com/stocks/quotes/SPY/options",
    "X-XSRF-TOKEN": "test" # Sometimes needed, sometimes not for initial handshake
}

params = {
    "symbol": "SPY",
    "fields": "symbol,strikePrice,lastPrice,volatility,openInterest,volume,tradeTime",
    "groupBy": "optionType",
    "expirationDate": "2025-01-17" # Approx date, usually they list all
}

try:
    # First get the page to get cookies (XSRF)
    s = requests.Session()
    r_home = s.get("https://www.barchart.com/stocks/quotes/SPY/options", headers=headers, timeout=10)
    print(f"Home Page Status: {r_home.status_code}")
    
    # Try the API
    # We need to find valid expiration dates first, but let's see if we get a 403 or 200 on the root options page
    if r_home.status_code == 200:
         print("[SUCCESS] Barchart website is accessible (Not Blocked).")
         print("This could be a valid alternative source.")
    elif r_home.status_code == 403:
         print("[FAIL] Barchart is blocking (403 Forbidden).")
    else:
         print(f"[?] Barchart Status: {r_home.status_code}")

except Exception as e:
    print(f"[ERROR] Failed to connect: {e}")
