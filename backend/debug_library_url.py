import requests
import json

def test_specific_login():
    url = "https://u1suser.webullfintech.com/api/user/v1/login/account/v2"
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json",
        "did": "1234567890123456",
        "app": "global",
        "platform": "web"
    }

    payload = {
        "account": "test@example.com",
        "accountType": 2,
        "pwd": "dummy_password",
        "regionId": 6
    }
    
    print(f"Testing {url}...")
    try:
        resp = requests.post(url, json=payload, headers=headers)
        print(f"Status: {resp.status_code}")
        print(resp.text[:200])
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test_specific_login()
