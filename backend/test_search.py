import requests
import json

def search_symbol(query):
    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&newsCount=0"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        resp = requests.get(url, headers=headers)
        data = resp.json()
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(e)

search_symbol("Apple")
search_symbol("Tesla")
