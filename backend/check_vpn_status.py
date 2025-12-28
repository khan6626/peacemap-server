import requests
import json

def check_vpn():
    print("--- CHECKING VPN STATUS ---")
    
    # 1. Check IP Location
    try:
        print("1. Checking Internet Location...")
        ip_info = requests.get("http://ip-api.com/json/", timeout=5).json()
        country = ip_info.get('country')
        ip = ip_info.get('query')
        print(f"   -> Detected Location: {country}")
        print(f"   -> IP: {ip}")
        
        if country != "United States":
            print("   [WARNING] You are NOT in the USA. connection might fail.")
        else:
            print("   [OK] Great! You appear to be in the USA.")
    except Exception as e:
        print(f"   [ERROR] Could not check IP: {e}")

    # 2. Check Webull Connectivity
    print("\n2. Checking Webull Server Connection...")
    url = "https://userapi.webullfintech.com/api/user/login/v3/byEmail"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "platform": "web",
        "app": "global",
        "ver": "4.0.0",
        "device-type": "Web"
    }
    
    try:
        # A simple payload to trigger a response
        payload = {"email": "test@test.com", "pwd": "password", "regionId": 6}
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        
        print(f"   -> Server Response Code: {resp.status_code}")
        
        if resp.status_code == 503:
            print("   [FAIL] Webull is BLOCKING this connection (503). VPN might be detected or not working.")
        elif resp.status_code == 403 and "Illegal" in resp.text:
             print(f"   [FAIL] 403 Illegal Client. Headers might need adjustment, but IP seems okayish.")
        elif resp.status_code == 200 or resp.status_code == 400:
            print("   [SUCCESS] Connected to Webull login server! (Response indicates we reached the API).")
        else:
            print(f"   [?] Response: {resp.status_code} - {resp.text[:100]}")
            
    except Exception as e:
        print(f"   [ERROR] Connection failed: {e}")

if __name__ == "__main__":
    check_vpn()
