import json
import os
import time
from webull import webull
import pandas as pd
from datetime import datetime

class WebullClient:
    def __init__(self, token_file='webull_session.json'):
        self.wb = webull()
        # Patch headers to avoid "Illegal Client" 403 error
        self.wb._session.headers.update({
            "User-Agent": "Webull/4.15.0 (iPhone; iOS 16.5; Scale/3.00)",
            "platform": "ios",
            "app": "global",
            "ver": "4.15.0",
            "device-type": "iPhone",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9"
        })
        self.token_file = token_file
        self.access_token = None
        self.refresh_token = None
        self.is_logged_in = False
        
        # PROXY SETUP
        try:
            if os.path.exists('magic_proxy.txt'):
                with open('magic_proxy.txt', 'r') as f:
                    proxy = f.read().strip()
                if proxy:
                    print(f"Using Proxy: {proxy}")
                    self.wb._session.proxies.update({
                        'http': proxy,
                        'https': proxy
                    })
        except Exception as e:
            print(f"Proxy Config Error: {e}")

        self._load_session()

    def _load_session(self):
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'r') as f:
                    data = json.load(f)
                    self.access_token = data.get('access_token')
                    self.refresh_token = data.get('refresh_token')
                    self.wb.set_tokens(self.access_token, self.refresh_token)
                    self.wb.refresh_login()
                    self.is_logged_in = True
                    print("Webull session loaded and refreshed.")
            except Exception as e:
                print(f"Failed to load Webull session: {e}")
                self.is_logged_in = False

    def _save_session(self):
        try:
            with open(self.token_file, 'w') as f:
                json.dump({
                    'access_token': self.wb.access_token,
                    'refresh_token': self.wb.refresh_token
                }, f)
            self.is_logged_in = True
        except Exception as e:
            print(f"Failed to save session: {e}")

    def login(self, username, password, mfa=None):
        try:
            if mfa:
                res = self.wb.login(username, password, mfa=mfa)
            else:
                res = self.wb.login(username, password)
            
            # DEBUG: Log login response
            try:
                with open('login_debug.log', 'w') as f:
                    f.write(json.dumps(res, indent=2))
            except:
                pass
            
            # Webull API response handling
            if 'accessToken' in res:
                self._save_session()
                return {'success': True}
            elif 'msg' in res and 'mfa' in res.get('msg', '').lower():
                 return {'success': False, 'mfa_required': True}
            else:
                # FALLBACK TO SELENIUM
                # If normal login failed (likely blocked), try the headless bypass
                print("API Login failed. Attempting Selenium Bypass...")
                try:
                    from bypass_login import run_headless_login
                    if run_headless_login(username, password, mfa):
                         # Reload session
                         self._load_session()
                         return {'success': True}
                except Exception as e:
                    print(f"Selenium Bypass Failed: {e}")

                return {'success': False, 'error': res.get('msg', 'Unknown login error')}
        except Exception as e:
            # DEBUG: Log exception
            try:
                with open('login_debug.log', 'w') as f:
                    f.write(str(e))
            except:
                pass
            
            error_msg = str(e)
            
            # Expanded Debugging for Blocked Requests
            if "Expecting value" in error_msg:
                error_msg = "Server IP Blocked (503). You MUST use a DESKTOP VPN app (not a browser extension) connected to USA."
            
            return {'success': False, 'error': error_msg}

    def get_ticker_id(self, symbol):
        try:
            return self.wb.get_ticker(symbol)['tickerId']
        except:
            return None

    def get_dates(self, symbol):
        if not self.is_logged_in:
            return []
        try:
            tid = self.get_ticker_id(symbol)
            if not tid: return []
            return [d['date'] for d in self.wb.get_options_expiration_dates(tid)]
        except Exception as e:
            print(f"Error fetching dates from Webull: {e}")
            return []

    def get_option_chain(self, symbol, date):
        if not self.is_logged_in:
            return None, None # calls, puts
        try:
            tid = self.get_ticker_id(symbol)
            if not tid: return None, None
            
            # Webull expects date in specific format, existing format matches?
            # webull dates are usually YYYY-MM-DD
            
            # Fetch options
            # This returns a complex structure, we need to flatten it
            # But wait, webull.get_options returns a list of options for that expiration
            # Let's see what the library returns.
            # It usually returns a list of dictionaries.
            
            options_data = self.wb.get_options(stock=tid, expireDate=date)
            # We need to separate calls and puts and format like the yfinance df
            
            calls = []
            puts = []
            
            for opt in options_data:
                # DEBUG: Log keys to file to find real-time volume field
                try:
                    with open('debug_log.txt', 'w') as f:
                        f.write(json.dumps(opt, indent=2))
                except:
                    pass

                # Key fields needed: strike, impliedVolatility, openInterest, volume, close (price)
                strike = float(opt.get('strikePrice', 0))
                is_call = opt.get('direction') == 'call'
                
                # Extract Greeks if available (Webull might not give Greeks in this call, might need get_option_greeks)
                # Actually, basic data typically includes some info. 
                # If 'delta' etc are missing, we might need to calculate them or request detail.
                # For GEX, we need IV (impVol) and Open Interest.
                
                # Check fields
                iv = 0
                if 'impVol' in opt: # Format might be 'impVol' or 'impliedVolatility'
                     iv = float(opt['impVol'])
                
                oi = int(opt.get('openInt', 0))
                vol = int(opt.get('volume', 0))
                
                row = {
                    'strike': strike,
                    'impliedVolatility': iv,
                    'openInterest': oi,
                    'volume': vol
                }
                
                if is_call:
                    calls.append(row)
                else:
                    puts.append(row)
                    
            return pd.DataFrame(calls), pd.DataFrame(puts)

        except Exception as e:
            print(f"Error fetching options from Webull: {e}")
            return None, None

    def get_spot_price(self, symbol):
        try:
            tid = self.get_ticker_id(symbol)
            quote = self.wb.get_quote(tid)
            return float(quote.get('close') or quote.get('price')) # 'close' is prev close? 'price' is current?
            # Actually 'pPrice' is usually current or 'price'.
            # Let's trust 'price' if available, else 'close'
        except:
            return 0.0
