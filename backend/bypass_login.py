import time
import json
import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def run_headless_login(username, password, mfa=None):
    print("Starting Headless Login...")
    
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Suppress logging
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # 1. Go to Login Page
        print("Navigating to Webull Login...")
        driver.get("https://app.webull.com/login")
        
        wait = WebDriverWait(driver, 20)
        
        # 2. Find and Fill Email
        print("Entering Credentials...")
        # Webull's login selectors might change, using generic attributes where possible
        # Typically inputs have type='email' or type='password'
        
        # Wait for email input
        email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[placeholder*='Email']")))
        email_input.clear()
        email_input.send_keys(username)
        
        pass_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        pass_input.clear()
        pass_input.send_keys(password)
        
        # 3. Click Login
        # Finding the login button can be tricky. Usually a button with type='submit' or text 'Log In'
        login_btn = driver.find_element(By.CSS_SELECTOR, "div[class*='login-btn'], button[type='submit']")
        login_btn.click()
        
        print("Clicked Login. Waiting...")
        
        # 4. Handle MFA (If needed - incomplete implementation for now, just waits)
        # We wait to see if we get logged in (URL change or specific element)
        
        # Wait for "Trade" or "Account" or redirect to trading terminal
        time.sleep(5)
        
        # Check for success
        current_url = driver.current_url
        print(f"Current URL: {current_url}")
        
        # 5. Extract Tokens from LocalStorage
        # Webull stores tokens in localStorage
        print("Extracting Tokens...")
        
        tokens = driver.execute_script("return window.localStorage;")
        
        access_token = tokens.get('access_token') or tokens.get('accessToken')
        refresh_token = tokens.get('refresh_token') or tokens.get('refreshToken')
        
        if not access_token:
            # Try Cookies
            print("LocalStorage empty, checking cookies...")
            cookies = driver.get_cookies()
            for cookie in cookies:
                if cookie['name'] == 'access_token':
                    access_token = cookie['value']
                if cookie['name'] == 'refresh_token':
                    refresh_token = cookie['value']

        if access_token:
            print("SUCCESS: Tokens Found!")
            session_data = {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'uuid': 'headless_generated'
            }
            
            with open('webull_session.json', 'w') as f:
                json.dump(session_data, f)
                
            return True
        else:
            print("FAILED: No tokens found. Likely MFA or Captcha triggered.")
            return False
            
    except Exception as e:
        print(f"Error in Headless Login: {e}")
        return False
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    # Test (replace args with env vars in prod)
    if len(sys.argv) > 2:
        u = sys.argv[1]
        p = sys.argv[2]
        run_headless_login(u, p)
