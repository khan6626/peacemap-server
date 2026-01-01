import time
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager

def main():
    print("===================================================")
    print("      WEBULL LOGIN TOOL v4 (Network Sniffer)       ")
    print("===================================================")
    print("This tool intercepts the 'keys' directly from the network traffic.")
    print("1. Chrome will open.")
    print("2. Log in manually.")
    print("3. Click on 'Watchlist' or any stock to trigger data.")
    print("4. Watch this window for SUCCESS.")
    print("===================================================")
    
    # Enable Performance Logging
    capabilities = DesiredCapabilities.CHROME
    capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
    
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    # Important for capturing network logs
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    
    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        print("Navigating to Webull Login...")
        driver.get("https://app.webull.com/login") 
        
        print("\nListening for secret keys in network traffic...")
        
        start_time = time.time()
        timeout = 600 # 10 minutes
        
        found_token = None
        found_did = None
        
        while time.time() - start_time < timeout:
            try:
                # Extract logs
                logs = driver.get_log("performance")
                
                for entry in logs:
                    message = json.loads(entry["message"])["message"]
                    
                    # specific method: Network.requestWillBeSent
                    if message["method"] == "Network.requestWillBeSent":
                        headers = message["params"]["request"]["headers"]
                        
                        # Look for Access Token in headers
                        # Common names: 'access_token', 'Authorization', 'did', 'device-id'
                        
                        # Check Token
                        token = headers.get("access_token") or headers.get("accessToken") or headers.get("Authorization")
                        if token:
                            if token.startswith("Bearer "): 
                                token = token.split(" ")[1]
                            
                            if len(token) > 50: # valid length check
                                found_token = token
                        
                        # Check DID
                        did = headers.get("did") or headers.get("device-id")
                        if did:
                            found_did = did
                            
                        # If we have both (or at least token), SUCCESS
                        if found_token:
                            print(f"\n[SNIFFER] Captured Token! (Length: {len(found_token)})")
                            if found_did:
                                print(f"[SNIFFER] Captured Device ID: {found_did}")
                            else:
                                print("[SNIFFER] Device ID not found yet (optional but good)...")
                                
                            # Save
                            data = {
                                'access_token': found_token,
                                'refresh_token': found_token, # Use same for now
                                'did': found_did,
                                'login_time': time.time(),
                                'uuid': 'sniffer_v4'
                            }
                            
                            current_dir = os.path.dirname(os.path.abspath(__file__))
                            save_path = os.path.join(current_dir, 'webull_session.json')
                            
                            with open(save_path, 'w') as f:
                                json.dump(data, f, indent=2)
                            
                            print("\n" + "="*40)
                            print(" SUCCESS! Session Saved.")
                            print(" You can close the browser and restart the server.")
                            print("="*40 + "\n")
                            
                            # Verify with client library immediately
                            try:
                                from webull_client import WebullClient
                                client = WebullClient(token_file=save_path)
                                if client.is_logged_in:
                                    print("Verification: PASSED.")
                                else:
                                    # If verification fails, it might be due to DID mismatch
                                    if found_did:
                                        client.wb._set_did(found_did)
                                        if client.is_logged_in:
                                             print("Verification: PASSED (With DID fix).")
                            except:
                                pass
                                
                            input("Press ENTER to exit...")
                            return

                time.sleep(0.5)
                
            except Exception as e:
                # print(e)
                pass
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

if __name__ == "__main__":
    main()
