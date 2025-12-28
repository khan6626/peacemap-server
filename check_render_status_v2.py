import requests
import json

# Use the correct key 'email' expected by app.py
url = "https://peacemap-server.onrender.com/api/webull/login"
payload = {"email": "test@test.com", "password": "password123", "mfa": "123456"}

print(f"Testing connectivity to: {url}")
try:
    response = requests.post(url, json=payload, timeout=20)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
    
    if "Server IP Blocked" in response.text or "You MUST use a DESKTOP VPN" in response.text:
        print("\n[RESULT] FAIL. The server is still BLOCKED or using old code.")
    elif "Expecting value" in response.text:
        print("\n[RESULT] FAIL. The server received non-JSON (503 Block) from Webull.")
    else:
        print("\n[RESULT] SUCCESS! The server contacted Webull and got a valid JSON response.")
        
except Exception as e:
    print(f"Error: {e}")
