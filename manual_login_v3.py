import time
import json
import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def find_token_in_data(data_dict):
    """Recursively search for values looking like JWT tokens."""
    for key, value in data_dict.items():
        if isinstance(value, str) and len(value) > 100 and value.startswith('ey'):
            return value, key
        # Sometimes it's a JSON string inside a value
        if isinstance(value, str) and value.startswith('{'):
            try:
                inner_dict = json.loads(value)
                if isinstance(inner_dict, dict):
                     t, k = find_token_in_data(inner_dict)
                     if t: return t, f"{key}->{k}"
            except:
                pass
    return None, None

def main():
    print("===================================================")
    print("      WEBULL LOGIN TOOL v3 (Deep Search)           ")
    print("===================================================")
    print("1. Chrome will open.")
    print("2. Log in manually.")
    print("3. I will search everywhere for the token.")
    print("===================================================")
    
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Use a persistent profile so login remembers?
    # user_data_dir = os.path.join(os.getcwd(), "chrome_profile")
    # options.add_argument(f"user-data-dir={user_data_dir}")
    
    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        print("Navigating to Webull Login...")
        driver.get("https://app.webull.com/login") 
        
        print("\nWaiting for you to log in...")
        
        start_time = time.time()
        timeout = 600 # 10 minutes
        
        while time.time() - start_time < timeout:
            try:
                # 1. SNAPSHOT ALL STORAGE
                ls_data = driver.execute_script("var ls = window.localStorage; var r = {}; for (var i = 0; i < ls.length; i++) { r[ls.key(i)] = ls.getItem(ls.key(i)); } return r;")
                ss_data = driver.execute_script("var ss = window.sessionStorage; var r = {}; for (var i = 0; i < ss.length; i++) { r[ss.key(i)] = ss.getItem(ss.key(i)); } return r;")
                cookies = {c['name']: c['value'] for c in driver.get_cookies()}
                
                # Combine all sources
                all_sources = {'LocalStorage': ls_data, 'SessionStorage': ss_data, 'Cookies': cookies}
                
                found_token = None
                found_refresh = None
                
                # SEARCH STRATEGY 1: Exact Keys
                if not found_token:
                    for source_name, data in all_sources.items():
                        for k in ['access_token', 'accessToken', 'token', 'webull-wa_accessToken']:
                            if k in data:
                                found_token = data[k]
                                print(f"Found token in {source_name} key '{k}'")
                                break
                        if found_token: break
                
                # SEARCH STRATEGY 2: Deep Pattern Search (JWT)
                if not found_token:
                    for source_name, data in all_sources.items():
                        t, k = find_token_in_data(data)
                        if t:
                            found_token = t
                            print(f"Deep Search found token in {source_name} at '{k}'")
                            break

                # SEARCH REFRESH TOKEN
                if found_token:
                    # Look for refresh token similar way
                    for source_name, data in all_sources.items():
                         for k in ['refresh_token', 'refreshToken', 'refresh']:
                             if k in data: 
                                 found_refresh = data[k]
                                 break
                    if not found_refresh: found_refresh = found_token # Fallback

                    # SAVE
                    data = {
                        'access_token': found_token,
                        'refresh_token': found_refresh,
                        'login_time': time.time(),
                        'uuid': 'manual_v3'
                    }
                    
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    save_path = os.path.join(current_dir, 'webull_session.json')
                    
                    with open(save_path, 'w') as f:
                        json.dump(data, f, indent=2)
                    
                    print("\n" + "="*40)
                    print(" SUCCESS! Token Captured.")
                    print("="*40 + "\n")
                    
                    # VERIFY
                    try:
                        from webull_client import WebullClient
                        client = WebullClient(token_file=save_path)
                        # Manually force loading it just created
                        client.access_token = found_token
                        client.refresh_token = found_refresh
                        
                        if client.is_logged_in:
                            print("Backend verified the token is valid.")
                        else:
                            print("Backend loaded token but connection check failed (might still work).")
                    except:
                        pass
                        
                    break
                
                time.sleep(1)
                
            except Exception as e:
                # print(e)
                time.sleep(1)
        else:
             print("\nTimeout.")

    except Exception as e:
        print(f"\nError: {e}")
    finally:
        print("\nClosing...")
        try:
            if driver: driver.quit()
        except:
            pass
        input("Press ENTER to exit...")

if __name__ == "__main__":
    main()
