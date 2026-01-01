import requests
import json

url = "https://peacemap-server.onrender.com/api/webull/login"
payload = {"username": "test@test.com", "password": "password", "mfa": "123456"}

print(f"Testing connectivity to: {url}")
try:
    response = requests.post(url, json=payload, timeout=15)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
    
    if "Server IP Blocked" in response.text:
        print("\n[RESULT] Still Blocked by Webull IP check.")
    elif "Unknown login error" in response.text or "success" in response.text or "account" in response.text.lower():
        print("\n[RESULT] SUCCESS! The server is NOT blocked (Standard login error received).")
    else:
        print("\n[RESULT] Received unexpected response (Server is reachable).")
        
except Exception as e:
    print(f"Error: {e}")
