import time
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def main():
    print("===================================================")
    print("      WEBULL LOGIN TOOL v2 (Robust Mode)           ")
    print("===================================================")
    print("1. A Google Chrome window will open.")
    print("2. Log in to your Webull account manually.")
    print("3. DO NOT close the window until THIS screen says SUCCESS.")
    print("===================================================")
    
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        print("Navigating to Webull...")
        driver.get("https://app.webull.com/watch") 
        
        print("\nWaiting for valid login session...")
        
        start_time = time.time()
        timeout = 600 # 10 minutes allow user to login
        
        while time.time() - start_time < timeout:
            try:
                # CHECK LOCAL STORAGE
                token = driver.execute_script("return window.localStorage.getItem('access_token') || window.localStorage.getItem('accessToken');")
                
                # CHECK COOKIES IF LS FAILS
                if not token:
                    cookies = driver.get_cookies()
                    for c in cookies:
                        if c['name'] == 'access_token': token = c['value']
                
                if token:
                    # Get Refresh Token
                    refresh = driver.execute_script("return window.localStorage.getItem('refresh_token') || window.localStorage.getItem('refreshToken');")
                    if not refresh:
                         cookies = driver.get_cookies()
                         for c in cookies:
                            if c['name'] == 'refresh_token': refresh = c['value']
                    
                    if not refresh: refresh = token # Fallback
                    
                    # Save
                    data = {
                        'access_token': token,
                        'refresh_token': refresh,
                        'login_time': time.time(),
                        'uuid': 'manual_v2'
                    }
                    
                    # Force save to current directory of this script
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    save_path = os.path.join(current_dir, 'webull_session.json')
                    
                    with open(save_path, 'w') as f:
                        json.dump(data, f, indent=2)
                    
                    print("\n" + "="*40)
                    print(" SUCCESS! Session Token Captured.")
                    print(f" Saved to: {save_path}")
                    print("="*40 + "\n")
                    
                    # VALIDATION
                    print("Validating session internally...")
                    try:
                        from webull_client import WebullClient
                        client = WebullClient(token_file=save_path)
                        if client.is_logged_in:
                            print("Verification: PASSED. Client is logged in.")
                            print("You can now restart your backend server.")
                        else:
                            print("Verification: WARNING. Token saved but client rejected it (Expired?).")
                    except Exception as ve:
                        print(f"Verification Check Failed: {ve}")

                    break
                
                time.sleep(2)
                print(".", end="", flush=True)
            except Exception as e:
                # print(e)
                time.sleep(2)
        else:
             print("\nTimeout: Login took too long.")

    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
    finally:
        print("\nClosing browser...")
        try:
            if driver: driver.quit()
        except:
            pass
        input("Press ENTER to exit...")

if __name__ == "__main__":
    main()
