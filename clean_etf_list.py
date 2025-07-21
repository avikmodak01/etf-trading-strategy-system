#!/usr/bin/env python3
"""
Clean ETF List - Remove unavailable/problematic ETFs
"""

import json
import shutil
from datetime import datetime
from etf_data_manager import ETFDataManager

def clean_etf_list():
    print("🧹 Cleaning ETF List")
    print("=" * 20)
    
    # Initialize
    data_manager = ETFDataManager()
    
    # Create backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"etf_data_backup_clean_{timestamp}.json"
    shutil.copy("etf_data.json", backup_file)
    print(f"📋 Backup created: {backup_file}")
    
    # List of ETFs to remove (known unavailable ones)
    etfs_to_remove = [
        'KOTAKLOVOL',  # No longer available
        # Add other unavailable ETFs here
    ]
    
    print(f"\n🔍 Scanning for problematic ETFs...")
    
    # Find ETFs with no price data (likely unavailable)
    problematic_etfs = []
    for etf_name, etf_data in data_manager.data["etfs"].items():
        if etf_data.get("cmp") is None and etf_data.get("dma_20") is None:
            problematic_etfs.append(etf_name)
    
    print(f"Found {len(problematic_etfs)} ETFs with no price data:")
    for etf in problematic_etfs:
        print(f"   - {etf}")
    
    # Combine lists
    all_etfs_to_remove = list(set(etfs_to_remove + problematic_etfs))
    
    print(f"\n🗑️ Removing {len(all_etfs_to_remove)} ETFs...")
    
    removed_count = 0
    kept_with_holdings = []
    
    for etf_name in all_etfs_to_remove:
        if etf_name not in data_manager.data["etfs"]:
            print(f"   ❌ {etf_name} not found")
            continue
        
        # Check for active holdings
        active_holdings = [
            h for h in data_manager.data["portfolio"] 
            if h["etf_name"] == etf_name and h["status"] == "active"
        ]
        
        if active_holdings:
            print(f"   ⚠️ Keeping {etf_name} - has {len(active_holdings)} active holdings")
            kept_with_holdings.append(etf_name)
            continue
        
        # Remove ETF
        del data_manager.data["etfs"][etf_name]
        print(f"   ✅ Removed {etf_name}")
        removed_count += 1
    
    # Save changes
    if removed_count > 0:
        data_manager._save_data()
        print(f"\n💾 Changes saved - removed {removed_count} ETFs")
    
    # Summary
    print(f"\n📊 Cleanup Summary:")
    print(f"   Total ETFs processed: {len(all_etfs_to_remove)}")
    print(f"   Successfully removed: {removed_count}")
    print(f"   Kept (has holdings): {len(kept_with_holdings)}")
    
    if kept_with_holdings:
        print(f"\n⚠️ ETFs kept due to active holdings:")
        for etf in kept_with_holdings:
            holdings = [
                h for h in data_manager.data["portfolio"] 
                if h["etf_name"] == etf and h["status"] == "active"
            ]
            total_qty = sum(h["quantity"] for h in holdings)
            print(f"   - {etf}: {total_qty} units across {len(holdings)} holdings")
    
    # Show final count
    final_count = len(data_manager.data["etfs"])
    print(f"\n📈 Final ETF count: {final_count}")
    
    return removed_count > 0

def show_etf_status():
    """Show current ETF status"""
    data_manager = ETFDataManager()
    
    print(f"\n📊 Current ETF Status:")
    print("=" * 25)
    
    total_etfs = len(data_manager.data["etfs"])
    with_prices = 0
    without_prices = []
    volume_qualified = 0
    
    for etf_name, etf_data in data_manager.data["etfs"].items():
        if etf_data.get("cmp") is not None:
            with_prices += 1
        else:
            without_prices.append(etf_name)
        
        if etf_data.get("volume_qualified") is True:
            volume_qualified += 1
    
    print(f"Total ETFs: {total_etfs}")
    print(f"With price data: {with_prices}")
    print(f"Without price data: {len(without_prices)}")
    print(f"Volume qualified: {volume_qualified}")
    
    if without_prices:
        print(f"\n⚠️ ETFs without price data:")
        for etf in without_prices[:10]:  # Show first 10
            print(f"   - {etf}")
        if len(without_prices) > 10:
            print(f"   ... and {len(without_prices) - 10} more")

if __name__ == "__main__":
    print("🧹 ETF List Cleanup Tool")
    print("=" * 30)
    
    # Show current status
    show_etf_status()
    
    # Perform cleanup
    success = clean_etf_list()
    
    if success:
        print("\n🎉 ETF list cleanup completed!")
        print("💡 Run enhanced_cli.py to see the updated list")
    else:
        print("\n💡 No changes made to ETF list")