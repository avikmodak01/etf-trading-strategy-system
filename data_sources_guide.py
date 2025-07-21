#!/usr/bin/env python3
"""
Comprehensive Guide to ETF Data Sources in India

This module provides various methods to fetch live and historical ETF prices
including free and paid APIs, web scraping, and CSV import methods.
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf
import json
from typing import Dict, List, Optional

class DataSourcesGuide:
    """Guide to different ETF data sources and how to use them"""
    
    def __init__(self):
        self.data_sources = {
            "yahoo_finance": {
                "name": "Yahoo Finance",
                "cost": "Free",
                "reliability": "High",
                "coverage": "Most Indian ETFs",
                "real_time": "15-min delay",
                "historical": "Yes",
                "api_key_required": "No"
            },
            "alpha_vantage": {
                "name": "Alpha Vantage",
                "cost": "Free (limited) / Paid",
                "reliability": "High",
                "coverage": "Limited Indian ETFs",
                "real_time": "Yes (paid)",
                "historical": "Yes",
                "api_key_required": "Yes"
            },
            "nse_website": {
                "name": "NSE Website Scraping",
                "cost": "Free",
                "reliability": "Medium (anti-bot measures)",
                "coverage": "All NSE ETFs",
                "real_time": "Yes",
                "historical": "Limited",
                "api_key_required": "No"
            },
            "zerodha_kite": {
                "name": "Zerodha Kite API",
                "cost": "₹2000/month",
                "reliability": "Very High",
                "coverage": "All Indian ETFs",
                "real_time": "Yes",
                "historical": "Yes",
                "api_key_required": "Yes"
            },
            "csv_import": {
                "name": "CSV Import from Broker",
                "cost": "Free",
                "reliability": "High",
                "coverage": "Based on broker",
                "real_time": "Manual update",
                "historical": "Yes",
                "api_key_required": "No"
            }
        }
    
    def display_data_sources_comparison(self):
        """Display comparison of all data sources"""
        print("📊 ETF Data Sources Comparison")
        print("=" * 80)
        
        headers = ["Source", "Cost", "Reliability", "Real-time", "Historical", "API Key"]
        print(f"{headers[0]:<20}{headers[1]:<15}{headers[2]:<12}{headers[3]:<12}{headers[4]:<12}{headers[5]}")
        print("-" * 80)
        
        for source_id, info in self.data_sources.items():
            print(f"{info['name']:<20}{info['cost']:<15}{info['reliability']:<12}{info['real_time']:<12}{info['historical']:<12}{info['api_key_required']}")
    
    def yahoo_finance_example(self):
        """Example of using Yahoo Finance API"""
        print("\n🔥 Yahoo Finance - RECOMMENDED (Free & Reliable)")
        print("=" * 55)
        
        code_example = '''
# Yahoo Finance Integration (Already implemented in price_fetcher.py)

import yfinance as yf

def fetch_etf_data(symbol):
    # Convert NSE symbol to Yahoo format
    yahoo_symbol = f"{symbol}.NS"
    
    ticker = yf.Ticker(yahoo_symbol)
    
    # Get current data
    info = ticker.info
    hist = ticker.history(period="1mo")
    
    current_price = hist['Close'].iloc[-1]
    ma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
    
    return {
        'current_price': current_price,
        'ma_20': ma_20,
        'volume': hist['Volume'].iloc[-1],
        'name': info.get('longName', symbol)
    }

# Usage
data = fetch_etf_data('GOLDBEES')
print(f"GOLDBEES: ₹{data['current_price']:.2f}")
        '''
        
        print("✅ Advantages:")
        print("   • Completely free")
        print("   • No API key required")
        print("   • Covers most Indian ETFs")
        print("   • Historical data available")
        print("   • Reliable and stable")
        
        print("\n❌ Limitations:")
        print("   • 15-minute delayed data")
        print("   • Some ETFs might not be available")
        
        print("\n💻 Code Example:")
        print(code_example)
    
    def alpha_vantage_example(self):
        """Example of using Alpha Vantage API"""
        print("\n💎 Alpha Vantage API")
        print("=" * 25)
        
        code_example = '''
# Alpha Vantage Integration

import requests

class AlphaVantageETF:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
    
    def get_etf_data(self, symbol):
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': f'{symbol}.BSE',  # or .NSE
            'apikey': self.api_key
        }
        
        response = requests.get(self.base_url, params=params)
        data = response.json()
        
        if 'Global Quote' in data:
            quote = data['Global Quote']
            return {
                'symbol': symbol,
                'price': float(quote['05. price']),
                'change_percent': float(quote['10. change percent'].replace('%', '')),
                'volume': int(quote['06. volume'])
            }
        return None
    
    def get_daily_data(self, symbol):
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': f'{symbol}.BSE',
            'apikey': self.api_key
        }
        
        response = requests.get(self.base_url, params=params)
        return response.json()

# Usage
av = AlphaVantageETF('YOUR_API_KEY')
data = av.get_etf_data('GOLDBEES')
        '''
        
        print("✅ Advantages:")
        print("   • Real-time data (paid plan)")
        print("   • Good API documentation")
        print("   • Technical indicators available")
        
        print("\n❌ Limitations:")
        print("   • Limited free tier (5 calls/minute, 500 calls/day)")
        print("   • Limited coverage of Indian ETFs")
        print("   • Requires API key")
        
        print("\n💰 Pricing:")
        print("   • Free: 5 calls/min, 500 calls/day")
        print("   • Premium: $49.99/month")
        
        print("\n🔑 Setup:")
        print("   1. Go to https://www.alphavantage.co/support/#api-key")
        print("   2. Sign up for free API key")
        print("   3. Use the key in your code")
        
        print("\n💻 Code Example:")
        print(code_example)
    
    def zerodha_kite_example(self):
        """Example of using Zerodha Kite API"""
        print("\n🏦 Zerodha Kite API - PROFESSIONAL GRADE")
        print("=" * 45)
        
        code_example = '''
# Zerodha Kite API Integration

from kiteconnect import KiteConnect

class ZerodhaETFData:
    def __init__(self, api_key, access_token):
        self.kite = KiteConnect(api_key=api_key)
        self.kite.set_access_token(access_token)
    
    def get_etf_price(self, instrument_token):
        # Get live price
        quote = self.kite.quote([instrument_token])
        return quote[str(instrument_token)]
    
    def get_historical_data(self, instrument_token, from_date, to_date):
        # Get historical data
        return self.kite.historical_data(
            instrument_token=instrument_token,
            from_date=from_date,
            to_date=to_date,
            interval="day"
        )
    
    def get_all_instruments(self):
        # Get all available instruments
        return self.kite.instruments("NSE")

# Usage (after authentication)
kite_data = ZerodhaETFData('your_api_key', 'access_token')
instruments = kite_data.get_all_instruments()

# Find ETF instrument tokens
etf_instruments = [i for i in instruments if i['instrument_type'] == 'ETF']
        '''
        
        print("✅ Advantages:")
        print("   • Real-time tick data")
        print("   • Complete market data")
        print("   • All Indian ETFs covered")
        print("   • Historical data with multiple timeframes")
        print("   • Official broker API")
        
        print("\n❌ Limitations:")
        print("   • Expensive (₹2000/month)")
        print("   • Requires Zerodha account")
        print("   • Complex authentication")
        
        print("\n💰 Pricing:")
        print("   • ₹2000/month per app")
        print("   • Requires active Zerodha trading account")
        
        print("\n🔑 Setup:")
        print("   1. Open Zerodha trading account")
        print("   2. Create app at https://developers.kite.trade/")
        print("   3. Pay ₹2000 monthly fee")
        print("   4. Implement OAuth authentication")
        
        print("\n💻 Code Example:")
        print(code_example)
    
    def nse_scraping_example(self):
        """Example of NSE website scraping"""
        print("\n🕷️  NSE Website Scraping")
        print("=" * 30)
        
        code_example = '''
# NSE Website Scraping (Already implemented in price_fetcher.py)

import requests
from bs4 import BeautifulSoup

class NSEScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_etf_data(self, symbol):
        url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
        
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://www.nseindia.com/',
        }
        
        try:
            response = self.session.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                return {
                    'symbol': symbol,
                    'current_price': data['priceInfo']['lastPrice'],
                    'change_percent': data['priceInfo']['pChange'],
                    'volume': data['marketDeptOrderBook']['totalTradedVolume']
                }
        except Exception as e:
            print(f"Error: {e}")
            return None

# Usage
scraper = NSEScraper()
data = scraper.get_etf_data('GOLDBEES')
        '''
        
        print("✅ Advantages:")
        print("   • Free and real-time")
        print("   • All NSE ETFs covered")
        print("   • No API key required")
        
        print("\n❌ Limitations:")
        print("   • Anti-bot measures")
        print("   • May break if website changes")
        print("   • Rate limiting required")
        print("   • Reliability issues")
        
        print("\n⚠️  Important Notes:")
        print("   • Use responsibly with rate limiting")
        print("   • Add proper error handling")
        print("   • Consider as backup option only")
        
        print("\n💻 Code Example:")
        print(code_example)
    
    def csv_import_example(self):
        """Example of CSV import from brokers"""
        print("\n📊 CSV Import from Brokers")
        print("=" * 35)
        
        print("📁 Supported Broker CSV Formats:")
        print("   • Zerodha Kite (Holdings export)")
        print("   • Upstox (Portfolio download)")
        print("   • ICICI Direct (Holdings report)")
        print("   • HDFC Securities (Portfolio summary)")
        print("   • Angel Broking (Holdings report)")
        
        print("\n📋 Typical CSV Format:")
        csv_example = '''
Symbol,LTP,Volume,Change%,Quantity,Avg_Price
GOLDBEES,81.73,7566902,0.70,100,80.50
NIFTYBEES,281.43,4485164,-0.49,50,285.20
BANKBEES,580.73,757347,-0.78,25,575.00
        '''
        print(csv_example)
        
        code_example = '''
# CSV Import (Already implemented in price_fetcher.py)

import pandas as pd

def import_from_broker_csv(csv_file):
    df = pd.read_csv(csv_file)
    
    etf_data = {}
    for _, row in df.iterrows():
        symbol = row['Symbol']
        current_price = row['LTP']
        volume = row.get('Volume', 0)
        
        etf_data[symbol] = {
            'current_price': current_price,
            'volume': volume,
            'last_updated': datetime.now().isoformat()
        }
    
    return etf_data

# Usage
data = import_from_broker_csv('holdings.csv')
        '''
        
        print("\n✅ Advantages:")
        print("   • Completely free")
        print("   • Accurate portfolio data")
        print("   • Works with any broker")
        print("   • No rate limits")
        
        print("\n❌ Limitations:")
        print("   • Manual update required")
        print("   • No automatic refresh")
        print("   • Format varies by broker")
        
        print("\n📝 How to Export from Brokers:")
        print("   1. Login to your broker platform")
        print("   2. Go to Portfolio/Holdings section")
        print("   3. Look for 'Export' or 'Download' option")
        print("   4. Choose CSV format")
        print("   5. Save and import into the system")
        
        print("\n💻 Code Example:")
        print(code_example)
    
    def integration_recommendations(self):
        """Provide recommendations for different use cases"""
        print("\n🎯 INTEGRATION RECOMMENDATIONS")
        print("=" * 40)
        
        print("🏠 FOR PERSONAL USE (RECOMMENDED):")
        print("   Primary: Yahoo Finance (free, reliable)")
        print("   Backup: CSV import from broker")
        print("   Manual: NSE scraping (occasional use)")
        
        print("\n💼 FOR SMALL BUSINESS:")
        print("   Primary: Yahoo Finance")
        print("   Secondary: Alpha Vantage (paid plan)")
        print("   Backup: CSV import")
        
        print("\n🏢 FOR PROFESSIONAL/TRADING FIRM:")
        print("   Primary: Zerodha Kite API")
        print("   Secondary: Alpha Vantage")
        print("   Backup: Multiple broker APIs")
        
        print("\n📈 IMPLEMENTATION PRIORITY:")
        print("   1. Yahoo Finance (implemented ✅)")
        print("   2. CSV Import (implemented ✅)")
        print("   3. NSE Scraping (implemented ✅)")
        print("   4. Alpha Vantage (optional)")
        print("   5. Zerodha Kite (for professionals)")
        
        print("\n⚡ QUICK START GUIDE:")
        print("   1. Use our existing Yahoo Finance integration")
        print("   2. Test with sample data first")
        print("   3. Set up automatic updates")
        print("   4. Add CSV import as backup")
        print("   5. Consider paid APIs for production use")


def main():
    """Main function to display the complete guide"""
    guide = DataSourcesGuide()
    
    print("📚 COMPLETE GUIDE TO ETF DATA SOURCES IN INDIA")
    print("=" * 60)
    
    guide.display_data_sources_comparison()
    guide.yahoo_finance_example()
    guide.alpha_vantage_example()
    guide.zerodha_kite_example()
    guide.nse_scraping_example()
    guide.csv_import_example()
    guide.integration_recommendations()
    
    print("\n🎉 SUMMARY:")
    print("   • Yahoo Finance: Best free option (already integrated)")
    print("   • CSV Import: Reliable manual method (already integrated)")
    print("   • NSE Scraping: Free but unreliable (already integrated)")
    print("   • Alpha Vantage: Good paid option for more features")
    print("   • Zerodha Kite: Professional grade (expensive)")
    
    print("\n✅ YOUR SYSTEM ALREADY INCLUDES:")
    print("   • Yahoo Finance integration with 20-day MA calculation")
    print("   • CSV import from broker data")
    print("   • NSE website scraping (backup)")
    print("   • Automatic price update scheduler")
    print("   • Historical data analysis")
    
    print("\n🚀 READY TO USE:")
    print("   Run: python3 enhanced_cli.py")
    print("   Choose option 6: 'Fetch Live Prices (Yahoo Finance)'")
    print("   Or option 8: 'Update All ETF Prices'")


if __name__ == "__main__":
    main()