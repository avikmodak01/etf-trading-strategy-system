#!/usr/bin/env python3
"""
ETF List Management - Add/Remove ETFs from the system
"""

import json
import shutil
from datetime import datetime
from etf_data_manager import ETFDataManager

class ETFListManager:
    def __init__(self):
        self.data_manager = ETFDataManager()
        
    def create_backup(self):
        """Create backup before making changes"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"etf_data_backup_manage_{timestamp}.json"
        shutil.copy("etf_data.json", backup_file)
        return backup_file
    
    def remove_etf(self, etf_name: str, force=False):
        """Remove an ETF from the system"""
        print(f"\n🗑️ Removing ETF: {etf_name}")
        
        if etf_name not in self.data_manager.data["etfs"]:
            print(f"   ❌ ETF '{etf_name}' not found in system")
            return False
        
        # Check for active holdings
        active_holdings = []
        for holding in self.data_manager.data["portfolio"]:
            if holding["etf_name"] == etf_name and holding["status"] == "active":
                active_holdings.append(holding)
        
        # Check for recent transactions
        recent_transactions = []
        for transaction in self.data_manager.data["transactions"]:
            if transaction["etf_name"] == etf_name:
                recent_transactions.append(transaction)
        
        if active_holdings and not force:
            print(f"   ⚠️ WARNING: {len(active_holdings)} active holdings found!")
            for holding in active_holdings:
                print(f"      - {holding['quantity']} units at ₹{holding['price']}")
            print(f"   💡 Use force=True to remove anyway, or sell holdings first")
            return False
        
        if recent_transactions:
            print(f"   📊 Found {len(recent_transactions)} transaction records")
            if not force:
                print(f"   💡 Use force=True to remove anyway (keeps transaction history)")
        
        # Remove ETF data
        del self.data_manager.data["etfs"][etf_name]
        
        # Handle portfolio holdings
        if active_holdings:
            print(f"   🗑️ Removing {len(active_holdings)} active holdings")
            self.data_manager.data["portfolio"] = [
                h for h in self.data_manager.data["portfolio"] 
                if not (h["etf_name"] == etf_name and h["status"] == "active")
            ]
        
        # Keep transaction history for audit purposes
        print(f"   📝 Keeping {len(recent_transactions)} transaction records for audit")
        
        print(f"   ✅ Successfully removed ETF: {etf_name}")
        return True
    
    def add_etf(self, etf_name: str, initial_price=None, initial_ma=None):
        """Add a new ETF to the system"""
        print(f"\n➕ Adding ETF: {etf_name}")
        
        if etf_name in self.data_manager.data["etfs"]:
            print(f"   ⚠️ ETF '{etf_name}' already exists in system")
            return False
        
        # Add ETF with initial data
        etf_data = {
            "name": etf_name,
            "cmp": initial_price,
            "dma_20": initial_ma,
            "last_price_update": None,
            "deviation_percent": None
        }
        
        self.data_manager.data["etfs"][etf_name] = etf_data
        print(f"   ✅ Successfully added ETF: {etf_name}")
        
        if initial_price is None:
            print(f"   💡 Remember to update price data for {etf_name}")
        
        return True
    
    def list_problematic_etfs(self):
        """List ETFs that might need attention"""
        print(f"\n🔍 Analyzing ETF List for Issues...")
        print("=" * 40)
        
        issues_found = []
        
        for etf_name, etf_data in self.data_manager.data["etfs"].items():
            issues = []
            
            # Check for missing price data
            if etf_data.get("cmp") is None:
                issues.append("No price data")
            
            # Check for very old price updates
            last_update = etf_data.get("last_price_update")
            if last_update:
                try:
                    update_date = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                    days_old = (datetime.now() - update_date.replace(tzinfo=None)).days
                    if days_old > 7:
                        issues.append(f"Price data {days_old} days old")
                except:
                    issues.append("Invalid date format")
            
            # Check for volume qualification issues
            volume_qualified = etf_data.get("volume_qualified")
            if volume_qualified is False:
                issues.append("Low volume (disqualified)")
            
            if issues:
                issues_found.append((etf_name, issues))
        
        if issues_found:
            print(f"📊 Found {len(issues_found)} ETFs with potential issues:")
            for etf_name, issues in issues_found:
                print(f"\n   🔸 {etf_name}:")
                for issue in issues:
                    print(f"      - {issue}")
        else:
            print("✅ All ETFs look good!")
        
        return issues_found
    
    def interactive_management(self):
        """Interactive ETF management interface"""
        print("🔧 ETF List Management Tool")
        print("=" * 30)
        
        while True:
            print(f"\nOptions:")
            print(f"1. Remove ETF")
            print(f"2. Add ETF")
            print(f"3. List problematic ETFs")
            print(f"4. Show current ETF count")
            print(f"5. Exit")
            
            choice = input(f"\nEnter choice (1-5): ").strip()
            
            if choice == '1':
                etf_name = input("Enter ETF name to remove: ").strip().upper()
                if etf_name:
                    backup_file = self.create_backup()
                    print(f"📋 Backup created: {backup_file}")
                    
                    force = input("Force removal even with active holdings? (y/n): ").lower() == 'y'
                    success = self.remove_etf(etf_name, force=force)
                    
                    if success:
                        self.data_manager._save_data()
                        print("💾 Changes saved to disk")
            
            elif choice == '2':
                etf_name = input("Enter new ETF name: ").strip().upper()
                if etf_name:
                    price_input = input("Enter initial price (optional, press Enter to skip): ").strip()
                    initial_price = float(price_input) if price_input else None
                    
                    ma_input = input("Enter initial 20-day MA (optional, press Enter to skip): ").strip()
                    initial_ma = float(ma_input) if ma_input else None
                    
                    backup_file = self.create_backup()
                    print(f"📋 Backup created: {backup_file}")
                    
                    success = self.add_etf(etf_name, initial_price, initial_ma)
                    
                    if success:
                        self.data_manager._save_data()
                        print("💾 Changes saved to disk")
            
            elif choice == '3':
                self.list_problematic_etfs()
            
            elif choice == '4':
                total_etfs = len(self.data_manager.data["etfs"])
                print(f"\n📊 Current ETF count: {total_etfs}")
                
                # Show some stats
                with_prices = sum(1 for etf in self.data_manager.data["etfs"].values() if etf.get("cmp") is not None)
                volume_qualified = sum(1 for etf in self.data_manager.data["etfs"].values() if etf.get("volume_qualified") is True)
                
                print(f"   ETFs with price data: {with_prices}")
                print(f"   Volume qualified ETFs: {volume_qualified}")
            
            elif choice == '5':
                print("👋 ETF management complete!")
                break
            
            else:
                print("❌ Invalid choice")

def quick_remove_etfs(etfs_to_remove):
    """Quick function to remove multiple ETFs"""
    manager = ETFListManager()
    backup_file = manager.create_backup()
    print(f"📋 Backup created: {backup_file}")
    
    removed_count = 0
    for etf_name in etfs_to_remove:
        if manager.remove_etf(etf_name, force=True):
            removed_count += 1
    
    if removed_count > 0:
        manager.data_manager._save_data()
        print(f"\n💾 Changes saved - removed {removed_count} ETFs")
    
    return removed_count

def main():
    """Main function"""
    print("🔧 ETF List Management")
    print("=" * 25)
    
    # Quick option to remove KOTAKLOVOL
    print("Quick action available:")
    print("R. Remove KOTAKLOVOL (known unavailable ETF)")
    print("I. Interactive management")
    
    choice = input("\nEnter choice (R/I): ").strip().upper()
    
    if choice == 'R':
        removed = quick_remove_etfs(['KOTAKLOVOL'])
        if removed > 0:
            print("✅ KOTAKLOVOL removed successfully!")
    elif choice == 'I':
        manager = ETFListManager()
        manager.interactive_management()
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()