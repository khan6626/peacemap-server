
import requests

url = "https://www.theocc.com/Market-Data/Market-Data-Reports/series-and-trading-data/series-search"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.theocc.com/"
}

try:
    print(f"Fetching {url}...")
    resp = requests.get(url, headers=headers, timeout=10)
    print(f"Status Code: {resp.status_code}")
    if resp.status_code == 200:
        print("Success! Page content preview:")
        print(resp.text[:500])
    else:
        print("Failed.")
except Exception as e:
    print(f"Error: {e}")
