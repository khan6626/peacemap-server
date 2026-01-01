from webull import webull
import pandas as pd
from datetime import datetime
import json
import os

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
                    
                    # Apply Captured Device ID
                    captured_did = data.get('did')
                    if captured_did:
                        print(f"Applying Captured Device ID: {captured_did}")
                        self.wb._set_did(captured_did)
                        self.wb._session.headers.update({"did": captured_did, "device-id": captured_did})

                    self.wb._access_token = self.access_token
                    self.wb._refresh_token = self.refresh_token
                    try:
                        self.wb.access_token = self.access_token
                        self.wb.refresh_token = self.refresh_token
                    except:
                        pass
                        
                    self.wb._session.headers.update({
                        "Authorization": f"Bearer {self.access_token}",
                        "access_token": self.access_token
                    })
                    
                    self.is_logged_in = True
                    print("Webull session loaded (Manual Set).")
            except Exception as e:
                print(f"Failed to load Webull session: {e}")
                self.is_logged_in = False

    def _save_session(self):
        try:
            with open(self.token_file, 'w') as f:
                json.dump({
                    'access_token': self.wb.access_token,
                    'refresh_token': self.wb.refresh_token,
                    'did': self.wb._get_did()
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
            
            if 'accessToken' in res:
                self._save_session()
                return {'success': True}
            elif 'msg' in res and 'mfa' in res.get('msg', '').lower():
                 return {'success': False, 'mfa_required': True}
            else:
                return {'success': False, 'error': res.get('msg', 'Unknown login error')}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_ticker_id(self, symbol):
        try:
            result = self.wb.get_ticker(symbol)
            if isinstance(result, int):
                return result
            if isinstance(result, dict) and 'tickerId' in result:
                return result['tickerId']
            return result
        except:
            return None

    def get_dates(self, symbol):
        # Auto-reload session
        if not self.is_logged_in:
            self._load_session()
            
        if not self.is_logged_in:
            return []
        try:
            # FIX: Pass symbol string directly. 
            raw_dates = self.wb.get_options_expiration_dates(symbol)
            return [d['date'] for d in raw_dates]
        except Exception as e:
            print(f"Error fetching dates from Webull: {e}")
            return []

    def get_option_chain(self, symbol, date):
        if not self.is_logged_in:
            self._load_session()
            
        if not self.is_logged_in:
            return None, None
        try:
            # FIX: Pass symbol string directly. 
            options_data = self.wb.get_options(stock=symbol, expireDate=date)
            
            calls = []
            puts = []
            
            for item in options_data:
                # Handle Paired Structure (Response has 'call' and 'put' objects)
                if 'call' in item or 'put' in item:
                    if 'call' in item:
                        calls.append(self._parse_row(item['call']))
                    if 'put' in item:
                        puts.append(self._parse_row(item['put']))
                
                # Handle Flat Structure (Fallback)
                else:
                    row = self._parse_row(item)
                    if item.get('direction') == 'call':
                        calls.append(row)
                    else:
                        puts.append(row)

            if not calls:
                calls_df = pd.DataFrame(columns=['strike', 'impliedVolatility', 'openInterest', 'volume'])
            else:
                calls_df = pd.DataFrame(calls)
            
            if not puts:
                puts_df = pd.DataFrame(columns=['strike', 'impliedVolatility', 'openInterest', 'volume'])
            else:
                puts_df = pd.DataFrame(puts)
                    
            return calls_df, puts_df

        except Exception as e:
            print(f"Error fetching options from Webull: {e}")
            return None, None

    def _parse_row(self, data):
        strike = float(data.get('strikePrice', 0))
        
        # IV
        iv = 0.0
        if 'impVol' in data: 
             iv = float(data['impVol'])
        elif 'impliedVolatility' in data:
             iv = float(data['impliedVolatility'])
        
        # Open Interest (support both keys)
        oi = 0
        if 'openInt' in data:
            oi = int(data['openInt'])
        elif 'openInterest' in data:
            oi = int(data['openInterest'])
            
        # Volume
        vol = int(data.get('volume', 0))
        
        return {
            'strike': strike,
            'impliedVolatility': iv,
            'openInterest': oi,
            'volume': vol
        }

    def get_spot_price(self, symbol):
        if not self.is_logged_in:
            self._load_session()
            
        try:
            try:
                quote = self.wb.get_quote(symbol)
            except:
                tid = self.get_ticker_id(symbol)
                quote = self.wb.get_quote(tid)
            
            price = quote.get('pPrice') or quote.get('price') or quote.get('close')
            return float(price) if price else 0.0
        except Exception as e:
            print(f"Error getting spot price: {e}")
            return 0.0
