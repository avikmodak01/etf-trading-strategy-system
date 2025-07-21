#!/usr/bin/env python3
"""
Volume Filter for ETF Trading Strategy
Filters ETFs based on daily trading volume threshold
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from etf_data_manager import ETFDataManager
from price_fetcher import PriceFetcher

class VolumeFilter:
    """Manages volume-based ETF qualification for trading"""
    
    def __init__(self, data_manager: ETFDataManager, price_fetcher: PriceFetcher = None):
        self.data_manager = data_manager
        self.price_fetcher = price_fetcher or PriceFetcher()
        self.volume_config_file = "volume_filter_config.json"
        self.load_volume_config()
    
    def load_volume_config(self):
        """Load volume filter configuration"""
        try:
            with open(self.volume_config_file, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            # Create default configuration
            self.config = {
                "minimum_volume_threshold": 50000,
                "volume_check_enabled": True,
                "volume_averaging_days": 5,  # Use 5-day average volume
                "last_volume_update": None,
                "qualified_etfs": [],
                "disqualified_etfs": [],
                "settings": {
                    "exclude_zero_volume": True,
                    "require_consecutive_volume": True,
                    "grace_period_days": 2  # Allow 2 days below threshold
                }
            }
            self.save_volume_config()
    
    def save_volume_config(self):
        """Save volume filter configuration"""
        self.config["last_volume_update"] = datetime.now().isoformat()
        with open(self.volume_config_file, 'w') as f:
            json.dump(self.config, f, indent=2, default=str)
    
    def set_volume_threshold(self, threshold: int):
        """Set minimum volume threshold"""
        print(f"📊 Setting volume threshold to {threshold:,}")
        self.config["minimum_volume_threshold"] = threshold
        self.save_volume_config()
        
        # Re-evaluate all ETFs with new threshold
        self.update_all_etf_volume_status()
    
    def fetch_etf_volume_data(self, etf_symbol: str) -> Optional[Dict]:
        """Fetch volume data for a specific ETF"""
        try:
            # Get recent price data which includes volume
            data = self.price_fetcher.fetch_yahoo_finance_data(etf_symbol, period="1mo")
            
            if data and data.get('volume'):
                # Get historical data for volume averaging
                historical = self.price_fetcher.fetch_historical_data(
                    etf_symbol, 
                    start_date=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                )
                
                volume_info = {
                    'symbol': etf_symbol,
                    'current_volume': data['volume'],
                    'current_price': data['current_price'],
                    'last_updated': datetime.now().isoformat()
                }
                
                # Calculate average volume if historical data available
                if historical is not None and not historical.empty:
                    recent_volumes = historical['Volume'].tail(self.config["volume_averaging_days"])
                    avg_volume = recent_volumes.mean()
                    volume_info['average_volume_5d'] = int(avg_volume) if not pd.isna(avg_volume) else data['volume']
                    volume_info['volume_history'] = recent_volumes.tolist()
                else:
                    volume_info['average_volume_5d'] = data['volume']
                
                return volume_info
                
        except Exception as e:
            print(f"❌ Error fetching volume for {etf_symbol}: {e}")
            return None
    
    def update_etf_volume_status(self, etf_symbol: str) -> bool:
        """Update volume status for a specific ETF"""
        volume_data = self.fetch_etf_volume_data(etf_symbol)
        
        if not volume_data:
            return False
        
        # Update ETF data with volume information
        if etf_symbol in self.data_manager.data["etfs"]:
            self.data_manager.data["etfs"][etf_symbol]["volume_data"] = volume_data
            
            # Determine qualification status
            avg_volume = volume_data.get('average_volume_5d', volume_data['current_volume'])
            is_qualified = avg_volume >= self.config["minimum_volume_threshold"]
            
            self.data_manager.data["etfs"][etf_symbol]["volume_qualified"] = is_qualified
            self.data_manager.data["etfs"][etf_symbol]["volume_last_check"] = datetime.now().isoformat()
            
            # Update qualified/disqualified lists
            if is_qualified:
                if etf_symbol not in self.config["qualified_etfs"]:
                    self.config["qualified_etfs"].append(etf_symbol)
                if etf_symbol in self.config["disqualified_etfs"]:
                    self.config["disqualified_etfs"].remove(etf_symbol)
            else:
                if etf_symbol not in self.config["disqualified_etfs"]:
                    self.config["disqualified_etfs"].append(etf_symbol)
                if etf_symbol in self.config["qualified_etfs"]:
                    self.config["qualified_etfs"].remove(etf_symbol)
            
            print(f"📊 {etf_symbol}: Volume {avg_volume:,} - {'✅ Qualified' if is_qualified else '❌ Disqualified'}")
            return True
        
        return False
    
    def update_all_etf_volume_status(self):
        """Update volume status for all ETFs"""
        print(f"\n📊 Updating Volume Status for All ETFs")
        print(f"Minimum Volume Threshold: {self.config['minimum_volume_threshold']:,}")
        print("-" * 50)
        
        etf_list = list(self.data_manager.data["etfs"].keys())
        qualified_count = 0
        total_processed = 0
        
        for i, etf_symbol in enumerate(etf_list, 1):
            print(f"Processing {i}/{len(etf_list)}: {etf_symbol}")
            
            if self.update_etf_volume_status(etf_symbol):
                total_processed += 1
                if self.data_manager.data["etfs"][etf_symbol].get("volume_qualified", False):
                    qualified_count += 1
            
            # Rate limiting
            if i % 10 == 0:
                print(f"   Progress: {i}/{len(etf_list)} completed...")
                import time
                time.sleep(2)  # Pause to avoid rate limiting
        
        # Save updated data
        self.data_manager._save_data()
        self.save_volume_config()
        
        print(f"\n✅ Volume Status Update Complete!")
        print(f"   Total ETFs processed: {total_processed}")
        print(f"   Qualified ETFs: {qualified_count}")
        print(f"   Disqualified ETFs: {total_processed - qualified_count}")
        
        return qualified_count, total_processed
    
    def get_qualified_etfs(self) -> List[str]:
        """Get list of volume-qualified ETFs"""
        if not self.config["volume_check_enabled"]:
            return list(self.data_manager.data["etfs"].keys())
        
        qualified = []
        for etf_symbol, etf_data in self.data_manager.data["etfs"].items():
            if etf_data.get("volume_qualified", False):
                qualified.append(etf_symbol)
        
        return qualified
    
    def get_disqualified_etfs(self) -> List[str]:
        """Get list of volume-disqualified ETFs"""
        disqualified = []
        for etf_symbol, etf_data in self.data_manager.data["etfs"].items():
            if etf_data.get("volume_qualified") == False:  # Explicitly False, not None
                disqualified.append(etf_symbol)
        
        return disqualified
    
    def get_volume_report(self) -> Dict:
        """Generate comprehensive volume report"""
        qualified_etfs = self.get_qualified_etfs()
        disqualified_etfs = self.get_disqualified_etfs()
        
        # Get volume statistics
        volume_stats = []
        for etf_symbol in qualified_etfs:
            etf_data = self.data_manager.data["etfs"][etf_symbol]
            volume_data = etf_data.get("volume_data", {})
            
            if volume_data:
                volume_stats.append({
                    'symbol': etf_symbol,
                    'current_volume': volume_data.get('current_volume', 0),
                    'average_volume': volume_data.get('average_volume_5d', 0),
                    'current_price': volume_data.get('current_price', 0)
                })
        
        # Sort by volume (highest first)
        volume_stats.sort(key=lambda x: x['average_volume'], reverse=True)
        
        return {
            'threshold': self.config["minimum_volume_threshold"],
            'total_etfs': len(self.data_manager.data["etfs"]),
            'qualified_count': len(qualified_etfs),
            'disqualified_count': len(disqualified_etfs),
            'qualified_etfs': qualified_etfs,
            'disqualified_etfs': disqualified_etfs,
            'volume_stats': volume_stats,
            'last_updated': self.config.get("last_volume_update"),
            'filter_enabled': self.config["volume_check_enabled"]
        }
    
    def display_volume_report(self):
        """Display formatted volume report"""
        report = self.get_volume_report()
        
        print(f"\n📊 ETF Volume Qualification Report")
        print("=" * 50)
        print(f"Minimum Volume Threshold: {report['threshold']:,}")
        print(f"Volume Filter Enabled: {report['filter_enabled']}")
        print(f"Last Updated: {report['last_updated'][:19] if report['last_updated'] else 'Never'}")
        
        print(f"\n📈 Summary:")
        print(f"   Total ETFs: {report['total_etfs']}")
        print(f"   ✅ Qualified: {report['qualified_count']}")
        print(f"   ❌ Disqualified: {report['disqualified_count']}")
        print(f"   📊 Qualification Rate: {(report['qualified_count']/report['total_etfs']*100):.1f}%")
        
        print(f"\n✅ Top 10 Qualified ETFs by Volume:")
        print(f"{'Rank':<5}{'ETF':<12}{'Avg Volume':<12}{'Current Vol':<12}{'Price'}")
        print("-" * 55)
        for i, etf in enumerate(report['volume_stats'][:10], 1):
            print(f"{i:<5}{etf['symbol']:<12}{etf['average_volume']:<12,}{etf['current_volume']:<12,}₹{etf['current_price']:.2f}")
        
        if report['disqualified_etfs']:
            print(f"\n❌ Disqualified ETFs (Volume < {report['threshold']:,}):")
            for i, etf in enumerate(report['disqualified_etfs'][:10], 1):
                etf_data = self.data_manager.data["etfs"][etf].get("volume_data", {})
                volume = etf_data.get('average_volume_5d', 0)
                print(f"   {i}. {etf}: {volume:,}")
            
            if len(report['disqualified_etfs']) > 10:
                print(f"   ... and {len(report['disqualified_etfs']) - 10} more")
    
    def enable_volume_filter(self, enabled: bool = True):
        """Enable or disable volume filtering"""
        self.config["volume_check_enabled"] = enabled
        self.save_volume_config()
        
        status = "enabled" if enabled else "disabled"
        print(f"📊 Volume filtering {status}")
        
        if enabled:
            print("✅ Only volume-qualified ETFs will be eligible for trading recommendations")
        else:
            print("⚠️ All ETFs will be eligible regardless of volume")


def main():
    """Main function for volume filter management"""
    print("📊 ETF Volume Filter Management")
    print("=" * 35)
    
    from etf_data_manager import ETFDataManager
    from price_fetcher import PriceFetcher
    
    # Initialize
    data_manager = ETFDataManager()
    price_fetcher = PriceFetcher()
    volume_filter = VolumeFilter(data_manager, price_fetcher)
    
    while True:
        print("\nOptions:")
        print("1. Update all ETF volume status")
        print("2. Set volume threshold")
        print("3. View volume report")
        print("4. Enable/disable volume filter")
        print("5. Update specific ETF volume")
        print("6. Export qualified ETFs list")
        print("7. Exit")
        
        choice = input("\nEnter choice (1-7): ").strip()
        
        if choice == '1':
            print("\n🔄 This will update volume data for all ETFs...")
            print("⚠️ This may take several minutes due to rate limiting")
            confirm = input("Continue? (y/n): ").lower()
            if confirm == 'y':
                volume_filter.update_all_etf_volume_status()
        
        elif choice == '2':
            try:
                threshold = int(input("Enter minimum volume threshold: "))
                volume_filter.set_volume_threshold(threshold)
            except ValueError:
                print("❌ Invalid number")
        
        elif choice == '3':
            volume_filter.display_volume_report()
        
        elif choice == '4':
            current_status = volume_filter.config["volume_check_enabled"]
            print(f"Current status: {'Enabled' if current_status else 'Disabled'}")
            new_status = input("Enable volume filter? (y/n): ").lower() == 'y'
            volume_filter.enable_volume_filter(new_status)
        
        elif choice == '5':
            etf_symbol = input("Enter ETF symbol: ").strip().upper()
            volume_filter.update_etf_volume_status(etf_symbol)
        
        elif choice == '6':
            qualified = volume_filter.get_qualified_etfs()
            print(f"\n📋 Qualified ETFs ({len(qualified)}):")
            for etf in qualified:
                print(f"   {etf}")
        
        elif choice == '7':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice")


if __name__ == "__main__":
    main()