from webull import webull
import json
import os
import time

def save_session(wb):
    data = {
        'access_token': wb.access_token,
        'refresh_token': wb.refresh_token,
        'did': wb._get_did(),
        'uuid': 'via_simple_login'
    }
    with open('webull_session.json', 'w') as f:
        json.dump(data, f, indent=2)
    print("\n[SUCCESS] Login successful! Session saved to 'webull_session.json'.")
    print("You can now close this window and run the server.")

def main():
    print("========================================")
    print("      SIMPLE WEBULL LOGIN (No Browser)  ")
    print("========================================")
    
    wb = webull()
    
    # 1. Ask for credentials
    email = input("Enter Webull Email: ").strip()
    password = input("Enter Webull Password: ").strip()
    
    print("\nAttempting login...")
    try:
        # Try login
        res = wb.login(email, password)
        
        # Check result
        if 'accessToken' in res:
            save_session(wb)
            return
            
        # Handle MFA (Security Code)
        # Usually looking for specific error keys indicating MFA needed
        if 'msg' in res and ('mfa' in res['msg'].lower() or 'code' in res['msg'].lower()):
            print("\n[!] MFA Security Code Required.")
            mfa_code = input("Enter the 6-digit code sent to your phone/email: ").strip()
            
            res = wb.login(email, password, mfa=mfa_code)
            if 'accessToken' in res:
                save_session(wb)
            else:
                print(f"\n[ERROR] Login failed after MFA: {res}")
                
        else:
            # Maybe the user has a trading PIN or device verification? 
            # The library usually handles device ID automatically.
            print(f"\n[ERROR] Login failed: {res}")
            print("Note: If you have a puzzle captcha, this method might not work. Use the browser method instead.")

    except Exception as e:
        print(f"\n[CRITICAL ERROR] {e}")

    input("\nPress ENTER to exit...")

if __name__ == '__main__':
    main()
