import requests
import concurrent.futures
import time
import json

print("\n--- WEULL PROXY HUNTER ---")
print("Searching for a working US Proxy that Webull accepts...")

def get_proxies():
    # Source 1: ProxyScrape
    try:
        url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=3000&country=US&ssl=yes&anonymity=elite"
        r = requests.get(url, timeout=5)
        p1 = r.text.strip().splitlines()
        print(f"Found {len(p1)} Elite US proxies from Source 1.")
    except: p1 = []
    
    # Source 2: Geonode (simulated list or another free api if available, stick to proxyscrape mostly for free reliability)
    return list(set(p1))

proxies_list = get_proxies()

good_proxy = None
headers = {
    "User-Agent": "Webull/4.15.0 (iPhone; iOS 16.5; Scale/3.00)",
    "platform": "ios",
    "app": "global",
    "device-type": "iPhone"
}

def test_proxy(proxy_addr):
    global good_proxy
    if good_proxy: return
    
    proxy_url = f"http://{proxy_addr}"
    proxies = {"http": proxy_url, "https": proxy_url}
    
    try:
        # Test 1: Check IP/Location (Fast)
        # r = requests.get("http://ip-api.com/json/", proxies=proxies, timeout=3).json()
        # if r['countryCode'] != 'US': return
        
        # Test 2: Webull Handshake
        # We verify against the login endpoint usually blocked
        url = "https://userapi.webullfintech.com/api/user/login/v3/byEmail"
        payload = {"email": "test", "pwd": "test"} # doesn't matter, just want non-503
        
        r = requests.post(url, json=payload, headers=headers, proxies=proxies, timeout=5)
        
        if r.status_code != 503 and r.status_code != 403:
            # If we get 400 or 200, we passed the firewall
            print(f"\n[!!!] FOUND WORKING PROXY: {proxy_addr} (Status: {r.status_code})")
            good_proxy = proxy_url
    except:
        pass

print(f"Testing {len(proxies_list)} proxies (this may take 30-60 seconds)...")

with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    executor.map(test_proxy, proxies_list)

if good_proxy:
    print(f"\n[SUCCESS] We found a magic key! Proxy: {good_proxy}")
    # Save it
    with open("magic_proxy.txt", "w") as f:
        f.write(good_proxy)
else:
    print("\n[FAIL] Scanned all proxies and Webull blocked them all. They are very strict today.")
