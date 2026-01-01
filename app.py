from flask import Flask, request, jsonify
from flask_cors import CORS
# import yfinance as yf # REMOVED
import numpy as np
from scipy.stats import norm
from datetime import datetime
from webull_client import WebullClient
import os

app = Flask(__name__)
CORS(app)

# Initialize Webull Client
wb_client = WebullClient()

# STRICT MODE: Webull Only
print(f"Server started in STRICT WEBULL MODE. Yahoo Finance fallback is DISABLED.")

def black_scholes_gamma(S, K, T, r, sigma):
    """
    Calculate Gamma using Black-Scholes formula.
    S: Spot Price
    K: Strike Price
    T: Time to expiration (in years)
    r: Risk-free rate
    sigma: Implied Volatility
    """
    try:
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
        return gamma
    except Exception as e:
        # print(f"Error calculating gamma: {e}")
        return 0.0

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        'source': 'webull',
        'webull_logged_in': wb_client.is_logged_in
    })

@app.route('/api/webull/login', methods=['POST'])
def webull_login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    mfa = data.get('mfa')
    
    result = wb_client.login(email, password, mfa)
    return jsonify(result)

@app.route('/dates', methods=['GET'])
def get_dates():
    ticker_symbol = request.args.get('ticker')
    if not ticker_symbol:
        return jsonify({'error': 'Ticker is required'}), 400
    
    ticker_symbol = ticker_symbol.upper()

    try:
        # Webull usually doesn't use ^ for indices
        if ticker_symbol.startswith('^'):
            ticker_symbol = ticker_symbol[1:]
        
        # Special case: Webull often prefers just 'SPX' or 'NDX'
        if ticker_symbol == 'SPX500': ticker_symbol = 'SPX'

        dates = wb_client.get_dates(ticker_symbol)
        
        if not dates:
             if not wb_client.is_logged_in:
                 return jsonify({'error': 'Webull login required'}), 401
             else:
                 return jsonify({'error': f'No options found for {ticker_symbol} on Webull'}), 404
                 
        return jsonify({'dates': dates})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/profile', methods=['GET'])
def get_profile():
    ticker_symbol = request.args.get('ticker')
    date = request.args.get('date')

    if not ticker_symbol or not date:
        return jsonify({'error': 'Ticker and date are required'}), 400

    ticker_symbol = ticker_symbol.upper()

    try:
        spot_price = 0
        calls = None
        puts = None

        # Webull Logic Only
        if ticker_symbol.startswith('^'):
            ticker_symbol = ticker_symbol[1:]
        if ticker_symbol == 'SPX500': ticker_symbol = 'SPX'

        if not wb_client.is_logged_in:
             return jsonify({'error': 'Webull login required'}), 401
        
        spot_price = wb_client.get_spot_price(ticker_symbol)
        calls, puts = wb_client.get_option_chain(ticker_symbol, date)
        
        if calls is None or puts is None:
             return jsonify({'error': 'Failed to fetch Webull data or no data available'}), 500

        # Combine strikes
        all_strikes = sorted(set(calls['strike']).union(set(puts['strike'])))
        
        profile = []
        
        # Parameters for BS
        exp_date = datetime.strptime(date, '%Y-%m-%d')
        today = datetime.now()
        
        # Ensure T is always positive
        days_diff = (exp_date - today).total_seconds() / (24*3600)
        T = days_diff / 365.0
        if T <= 1e-5: T = 1e-5
        
        r = 0.045
        
        # Optimization: Create lookups
        calls_map = calls.set_index('strike').to_dict('index')
        puts_map = puts.set_index('strike').to_dict('index')

        for strike in all_strikes:
            
            # Call GEX
            call_gex = 0
            call_oi = 0
            call_vol = 0
            if strike in calls_map:
                row = calls_map[strike]
                sigma = row['impliedVolatility']
                call_oi = row['openInterest'] if not np.isnan(row['openInterest']) else 0
                call_vol = row['volume'] if not np.isnan(row['volume']) else 0
                
                if sigma > 0 and call_oi > 0:
                    gamma = black_scholes_gamma(spot_price, strike, T, r, sigma)
                    call_gex = gamma * call_oi * 100 * spot_price

            # Put GEX
            put_gex = 0
            put_oi = 0
            put_vol = 0
            if strike in puts_map:
                row = puts_map[strike]
                sigma = row['impliedVolatility']
                put_oi = row['openInterest'] if not np.isnan(row['openInterest']) else 0
                put_vol = row['volume'] if not np.isnan(row['volume']) else 0
                
                if sigma > 0 and put_oi > 0:
                    gamma = black_scholes_gamma(spot_price, strike, T, r, sigma)
                    # Put GEX is negative
                    put_gex = gamma * put_oi * 100 * spot_price * -1

            net_gex = call_gex + put_gex
            abs_gex = abs(call_gex) + abs(put_gex)
            
            if call_gex != 0 or put_gex != 0:
                profile.append({
                    'strike': strike,
                    'call_gex': call_gex,
                    'put_gex': put_gex,
                    'net_gex': net_gex,
                    'abs_gex': abs_gex,
                    'call_oi': call_oi,
                    'put_oi': put_oi,
                    'call_vol': call_vol,
                    'put_vol': put_vol
                })

        return jsonify({
            'spot_price': spot_price,
            'source': 'webull',
            'profile': profile
        })

    except Exception as e:
        print(f"Error in profile: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/search', methods=['GET'])
def search_ticker():
    query = request.args.get('q')
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    # We still use Yahoo for quick symbol search/autocomplete because it's an open public API.
    # However, we only care about the symbol string.
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&newsCount=0"
        headers = {'User-Agent': 'Mozilla/5.0'}
        import requests
        resp = requests.get(url, headers=headers)
        data = resp.json()
        
        results = []
        if 'quotes' in data:
            for q in data['quotes']:
                if 'symbol' in q:
                    # Clean symbol for Webull (remove ^ for indices)
                    sym = q['symbol']
                    if sym == '^SPX': sym = 'SPX'
                    if sym == '^NDX': sym = 'NDX'
                    if sym == '^VIX': sym = 'VIX'
                    if sym == '^RUT': sym = 'RUT'
                    if sym.startswith('^'): sym = sym[1:] # Generic rule
                    
                    results.append({
                        'symbol': sym,
                        'shortname': q.get('shortname', q.get('longname', ''))
                    })
        return jsonify({'results': results})
    except Exception as e:
        print(f"Search error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
