#!/usr/bin/env python3
"""
ETF Price Fetcher Module
Supports multiple data sources for fetching live and historical ETF prices
"""

import yfinance as yf
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time
import json
from bs4 import BeautifulSoup
import re

class PriceFetcher:
    """Fetches ETF prices from multiple data sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # NSE ETF symbol mapping (NSE symbol -> Yahoo Finance symbol)
        self.nse_to_yahoo_mapping = {
            'GOLDBEES': 'GOLDBEES.NS',
            'KOTAKGOLD': 'KOTAKGOLD.NS',
            'SETFGOLD': 'SETFGOLD.NS',
            'HNGSNGBEES': 'HNGSNGBEES.NS',
            'MAHKTECH': 'MAHKTECH.NS',
            'ITBEES': 'ITBEES.NS',
            'BANKBEES': 'BANKBEES.NS',
            'NIFTYBEES': 'NIFTYBEES.NS',
            'JUNIORBEES': 'JUNIORBEES.NS',
            'LIQUIDBEES': 'LIQUIDBEES.NS',
            'CPSE': 'CPSEETF.NS',
            'SILVRBEES': 'SILVRBEES.NS',
            'BHARATBOND': 'BHARATBOND.NS',
            'PSUBNKBEES': 'PSUBNKBEES.NS',
            'PVTBNKBEES': 'PVTBNKBEES.NS'
        }
    
    def fetch_yahoo_finance_data(self, symbol: str, period: str = "1mo") -> Optional[Dict]:
        """
        Fetch ETF data from Yahoo Finance
        
        Args:
            symbol: ETF symbol (will be converted to Yahoo format)
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        
        Returns:
            Dictionary with price data and moving averages
        """
        try:
            # Convert NSE symbol to Yahoo Finance format
            if symbol in self.nse_to_yahoo_mapping:
                yahoo_symbol = self.nse_to_yahoo_mapping[symbol]
            elif not symbol.endswith('.NS'):
                yahoo_symbol = f"{symbol}.NS"
            else:
                yahoo_symbol = symbol
            
            print(f"Fetching data for {symbol} ({yahoo_symbol}) from Yahoo Finance...")
            
            ticker = yf.Ticker(yahoo_symbol)
            
            # Get historical data
            hist = ticker.history(period=period)
            
            if hist.empty:
                print(f"No data found for {yahoo_symbol}")
                return None
            
            # Get current price (latest close)
            current_price = float(hist['Close'].iloc[-1])
            
            # Calculate moving averages
            ma_20 = float(hist['Close'].rolling(window=20).mean().iloc[-1])
            ma_50 = float(hist['Close'].rolling(window=50).mean().iloc[-1]) if len(hist) >= 50 else None
            
            # Get basic info
            info = ticker.info
            
            result = {
                'symbol': symbol,
                'yahoo_symbol': yahoo_symbol,
                'current_price': round(current_price, 2),
                'ma_20': round(ma_20, 2) if not pd.isna(ma_20) else None,
                'ma_50': round(ma_50, 2) if ma_50 and not pd.isna(ma_50) else None,
                'volume': int(hist['Volume'].iloc[-1]) if not pd.isna(hist['Volume'].iloc[-1]) else 0,
                'prev_close': float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price,
                'change_percent': 0,
                'last_updated': datetime.now().isoformat(),
                'data_source': 'yahoo_finance',
                'name': info.get('longName', symbol)
            }
            
            # Calculate change percentage
            if len(hist) > 1:
                prev_close = float(hist['Close'].iloc[-2])
                result['change_percent'] = round(((current_price - prev_close) / prev_close) * 100, 2)
            
            return result
            
        except Exception as e:
            print(f"Error fetching Yahoo Finance data for {symbol}: {e}")
            return None
    
    def fetch_nse_data(self, symbol: str) -> Optional[Dict]:
        """
        Fetch ETF data from NSE website (web scraping)
        Note: NSE has anti-bot measures, so this might not always work
        """
        try:
            # NSE API endpoint for ETF data
            url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': 'https://www.nseindia.com/',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'priceInfo' in data:
                    price_info = data['priceInfo']
                    
                    result = {
                        'symbol': symbol,
                        'current_price': float(price_info.get('lastPrice', 0)),
                        'prev_close': float(price_info.get('previousClose', 0)),
                        'change_percent': float(price_info.get('pChange', 0)),
                        'volume': int(data.get('marketDeptOrderBook', {}).get('totalTradedVolume', 0)),
                        'last_updated': datetime.now().isoformat(),
                        'data_source': 'nse',
                        'name': data.get('info', {}).get('companyName', symbol)
                    }
                    
                    return result
            
            return None
            
        except Exception as e:
            print(f"Error fetching NSE data for {symbol}: {e}")
            return None
    
    def fetch_historical_data(self, symbol: str, start_date: str, end_date: str = None) -> Optional[pd.DataFrame]:
        """
        Fetch historical price data for moving average calculations
        
        Args:
            symbol: ETF symbol
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format (defaults to today)
        
        Returns:
            DataFrame with historical prices
        """
        try:
            if end_date is None:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            # Use Yahoo Finance for historical data
            yahoo_symbol = self.nse_to_yahoo_mapping.get(symbol, f"{symbol}.NS")
            
            ticker = yf.Ticker(yahoo_symbol)
            hist = ticker.history(start=start_date, end=end_date)
            
            if not hist.empty:
                # Calculate moving averages
                hist['MA_5'] = hist['Close'].rolling(window=5).mean()
                hist['MA_10'] = hist['Close'].rolling(window=10).mean()
                hist['MA_20'] = hist['Close'].rolling(window=20).mean()
                hist['MA_50'] = hist['Close'].rolling(window=50).mean()
                
                return hist
            
            return None
            
        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {e}")
            return None
    
    def calculate_moving_averages(self, symbol: str, periods: List[int] = [20, 50]) -> Dict:
        """
        Calculate moving averages for the given periods
        
        Args:
            symbol: ETF symbol
            periods: List of periods for moving averages (default: [20, 50])
        
        Returns:
            Dictionary with moving averages
        """
        try:
            # Get 60 days of data to ensure we have enough for 50-day MA
            end_date = datetime.now()
            start_date = end_date - timedelta(days=80)  # Extra buffer
            
            hist_data = self.fetch_historical_data(
                symbol, 
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            
            if hist_data is None or hist_data.empty:
                return {}
            
            result = {}
            for period in periods:
                if len(hist_data) >= period:
                    ma_value = hist_data['Close'].rolling(window=period).mean().iloc[-1]
                    result[f'ma_{period}'] = round(float(ma_value), 2) if not pd.isna(ma_value) else None
            
            return result
            
        except Exception as e:
            print(f"Error calculating moving averages for {symbol}: {e}")
            return {}
    
    def fetch_multiple_etfs(self, etf_list: List[str], source: str = "yahoo") -> Dict[str, Dict]:
        """
        Fetch data for multiple ETFs
        
        Args:
            etf_list: List of ETF symbols
            source: Data source ("yahoo" or "nse")
        
        Returns:
            Dictionary with ETF data
        """
        results = {}
        
        for i, symbol in enumerate(etf_list):
            print(f"Processing {i+1}/{len(etf_list)}: {symbol}")
            
            if source == "yahoo":
                data = self.fetch_yahoo_finance_data(symbol)
            elif source == "nse":
                data = self.fetch_nse_data(symbol)
            else:
                # Try Yahoo first, fallback to NSE
                data = self.fetch_yahoo_finance_data(symbol)
                if data is None:
                    data = self.fetch_nse_data(symbol)
            
            if data:
                results[symbol] = data
            
            # Rate limiting to avoid being blocked
            time.sleep(1)
        
        return results
    
    def import_from_csv(self, csv_file: str, symbol_col: str = "Symbol", 
                       price_col: str = "LTP", volume_col: str = "Volume") -> Dict[str, Dict]:
        """
        Import ETF data from CSV file (e.g., exported from broker or NSE)
        
        Args:
            csv_file: Path to CSV file
            symbol_col: Column name for ETF symbols
            price_col: Column name for current price
            volume_col: Column name for volume data
        
        Returns:
            Dictionary with ETF data
        """
        try:
            df = pd.read_csv(csv_file)
            results = {}
            
            for _, row in df.iterrows():
                symbol = str(row[symbol_col]).strip()
                current_price = float(row[price_col])
                volume = int(row.get(volume_col, 0)) if volume_col in row else 0
                
                # Calculate moving averages
                ma_data = self.calculate_moving_averages(symbol)
                
                results[symbol] = {
                    'symbol': symbol,
                    'current_price': current_price,
                    'ma_20': ma_data.get('ma_20'),
                    'ma_50': ma_data.get('ma_50'),
                    'volume': volume,
                    'last_updated': datetime.now().isoformat(),
                    'data_source': 'csv_import'
                }
            
            return results
            
        except Exception as e:
            print(f"Error importing from CSV: {e}")
            return {}
    
    def get_etf_info(self, symbol: str) -> Optional[Dict]:
        """
        Get detailed ETF information
        """
        try:
            yahoo_symbol = self.nse_to_yahoo_mapping.get(symbol, f"{symbol}.NS")
            ticker = yf.Ticker(yahoo_symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'N/A'),
                'category': info.get('category', 'ETF'),
                'expense_ratio': info.get('annualReportExpenseRatio', 'N/A'),
                'net_assets': info.get('totalAssets', 'N/A'),
                'inception_date': info.get('fundInceptionDate', 'N/A'),
                'benchmark': info.get('benchmark', 'N/A')
            }
            
        except Exception as e:
            print(f"Error fetching ETF info for {symbol}: {e}")
            return None


class PriceUpdateScheduler:
    """Scheduler for automatic price updates"""
    
    def __init__(self, data_manager, price_fetcher):
        self.data_manager = data_manager
        self.price_fetcher = price_fetcher
        self.is_running = False
    
    def update_all_etf_prices(self, etf_list: List[str] = None):
        """Update prices for all ETFs in the portfolio"""
        try:
            if etf_list is None:
                etf_list = list(self.data_manager.data["etfs"].keys())
            
            if not etf_list:
                print("No ETFs found to update")
                return
            
            print(f"Updating prices for {len(etf_list)} ETFs...")
            
            # Fetch data from Yahoo Finance
            price_data = self.price_fetcher.fetch_multiple_etfs(etf_list, source="yahoo")
            
            updated_count = 0
            for symbol, data in price_data.items():
                if data and data.get('current_price') and data.get('ma_20'):
                    self.data_manager.update_etf_price(
                        symbol, 
                        data['current_price'], 
                        data['ma_20']
                    )
                    updated_count += 1
                    print(f"✅ Updated {symbol}: ₹{data['current_price']:.2f} (20MA: ₹{data['ma_20']:.2f})")
            
            print(f"\n🎉 Successfully updated {updated_count} ETFs!")
            return updated_count
            
        except Exception as e:
            print(f"Error updating ETF prices: {e}")
            return 0
    
    def schedule_regular_updates(self):
        """Schedule regular price updates (requires manual triggering for now)"""
        import schedule
        
        # Schedule updates during market hours (9:30 AM to 3:30 PM IST)
        schedule.every().monday.at("09:35").do(self.update_all_etf_prices)
        schedule.every().monday.at("12:00").do(self.update_all_etf_prices)
        schedule.every().monday.at("15:25").do(self.update_all_etf_prices)
        
        # Add for other weekdays
        for day in ['tuesday', 'wednesday', 'thursday', 'friday']:
            getattr(schedule.every(), day).at("09:35").do(self.update_all_etf_prices)
            getattr(schedule.every(), day).at("12:00").do(self.update_all_etf_prices)
            getattr(schedule.every(), day).at("15:25").do(self.update_all_etf_prices)
        
        print("📅 Price update schedule configured:")
        print("   - Market open: 9:35 AM")
        print("   - Mid-day: 12:00 PM") 
        print("   - Market close: 3:25 PM")
        print("   - Monday to Friday only")
        
        self.is_running = True
        
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute


def demo_price_fetching():
    """Demo function to show price fetching capabilities"""
    print("🚀 ETF Price Fetching Demo")
    print("=" * 40)
    
    fetcher = PriceFetcher()
    
    # Test ETFs
    test_etfs = ['GOLDBEES', 'NIFTYBEES', 'BANKBEES', 'ITBEES']
    
    print("\n1️⃣ Fetching data from Yahoo Finance:")
    print("-" * 40)
    
    for etf in test_etfs:
        data = fetcher.fetch_yahoo_finance_data(etf)
        if data:
            print(f"✅ {etf}:")
            print(f"   Current Price: ₹{data['current_price']}")
            print(f"   20-day MA: ₹{data['ma_20']}")
            print(f"   Volume: {data['volume']:,}")
            print(f"   Change: {data['change_percent']:.2f}%")
        else:
            print(f"❌ Failed to fetch data for {etf}")
        print()
    
    print("\n2️⃣ Calculating historical moving averages:")
    print("-" * 40)
    
    for etf in test_etfs[:2]:  # Test first 2 ETFs
        ma_data = fetcher.calculate_moving_averages(etf, [5, 10, 20, 50])
        if ma_data:
            print(f"✅ {etf} Moving Averages:")
            for period, value in ma_data.items():
                print(f"   {period.upper()}: ₹{value:.2f}" if value else f"   {period.upper()}: N/A")
        print()
    
    print("\n3️⃣ ETF Information:")
    print("-" * 40)
    
    info = fetcher.get_etf_info('GOLDBEES')
    if info:
        print(f"📊 {info['symbol']} ({info['name']}):")
        print(f"   Category: {info['category']}")
        print(f"   Sector: {info['sector']}")


if __name__ == "__main__":
    demo_price_fetching()