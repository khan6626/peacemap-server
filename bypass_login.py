import time
import json
import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def run_headless_login(username, password, mfa=None):
    print("Starting Login Bypass (Browser Mode)...")
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Avoid detection
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        print("Navigating to Webull Login...")
        driver.get("https://app.webull.com/login")
        
        print("\n" + "="*50)
        print("ACTION REQUIRED: Log in manually in the Chrome window.")
        print("The system is watching for your login session...")
        print("="*50 + "\n")
        
        # Poll for tokens instead of blocking input
        start_time = time.time()
        max_duration = 300 # 5 minutes
        access_token = None
        refresh_token = None
        
        while time.time() - start_time < max_duration:
            try:
                # Try LocalStorage
                ls_tokens = driver.execute_script("var ls = window.localStorage; var r = {}; for (var i = 0; i < ls.length; i++) { r[ls.key(i)] = ls.getItem(ls.key(i)); } return r;")
                
                access_token = ls_tokens.get('access_token') or ls_tokens.get('accessToken')
                refresh_token = ls_tokens.get('refresh_token') or ls_tokens.get('refreshToken')

                # Try SessionStorage
                if not access_token:
                    ss_tokens = driver.execute_script("var ss = window.sessionStorage; var r = {}; for (var i = 0; i < ss.length; i++) { r[ss.key(i)] = ss.getItem(ss.key(i)); } return r;")
                    access_token = ss_tokens.get('access_token') or ss_tokens.get('accessToken')
                    refresh_token = ss_tokens.get('refresh_token') or ss_tokens.get('refreshToken')

                # Try Cookies
                if not access_token:
                    cookies = driver.get_cookies()
                    for cookie in cookies:
                        if cookie['name'] == 'access_token': access_token = cookie['value']
                        if cookie['name'] == 'refresh_token': refresh_token = cookie['value']
                
                # Try finding ANY token that looks long enough
                if not access_token:
                     all_values = list(ls_tokens.values()) if ls_tokens else []
                     for v in all_values:
                         if isinstance(v, str) and len(v) > 100 and v.startswith("ey"):
                             access_token = v
                             break

                # SUCCESS CHECK
                if access_token:
                     print("\nSUCCESS: Login detected! Token captured.")
                     break
                
                time.sleep(2)
            except Exception as e:
                # print(f"Polling error: {e}")
                time.sleep(2)
        
        if access_token:
            if not refresh_token: refresh_token = access_token
            
            with open('webull_session.json', 'w') as f:
                json.dump({'access_token': access_token, 'refresh_token': refresh_token, 'uuid': 'manual_login'}, f)
            print("Session saved to webull_session.json")
            return True
        else:
            print("\nFAILED: No tokens found (Timeout).")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if driver: 
            try:
                driver.quit()
            except:
                pass

if __name__ == "__main__":
    run_headless_login("", "")
