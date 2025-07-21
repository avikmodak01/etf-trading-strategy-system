#!/usr/bin/env python3
"""
Restore the renamed ETFs that were accidentally removed
"""

import json
import shutil
from datetime import datetime
from etf_data_manager import ETFDataManager

def restore_renamed_etfs():
    print("🔄 Restoring Renamed ETFs")
    print("=" * 25)
    
    # Initialize
    data_manager = ETFDataManager()
    
    # Create backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"etf_data_backup_restore_{timestamp}.json"
    shutil.copy("etf_data.json", backup_file)
    print(f"📋 Backup created: {backup_file}")
    
    # ETFs to restore (the renamed ones that should exist)
    etfs_to_restore = {
        "ALPHA": {"name": "ALPHA"},
        "IT": {"name": "IT"},
        "NV20": {"name": "NV20"},
        "PSUBANK": {"name": "PSUBANK"}
    }
    
    print(f"\n➕ Restoring {len(etfs_to_restore)} renamed ETFs...")
    
    restored_count = 0
    for etf_name, etf_data in etfs_to_restore.items():
        if etf_name in data_manager.data["etfs"]:
            print(f"   ✅ {etf_name} already exists")
            continue
        
        # Add ETF with placeholder data
        data_manager.data["etfs"][etf_name] = {
            "name": etf_name,
            "cmp": None,
            "dma_20": None,
            "last_price_update": None,
            "deviation_percent": None
        }
        
        print(f"   ✅ Restored {etf_name}")
        restored_count += 1
    
    # Save changes
    if restored_count > 0:
        data_manager._save_data()
        print(f"\n💾 Changes saved - restored {restored_count} ETFs")
    
    print(f"\n📊 Restoration Summary:")
    print(f"   ETFs restored: {restored_count}")
    print(f"   Total ETFs now: {len(data_manager.data['etfs'])}")
    
    return restored_count > 0

def remove_only_kotaklovol():
    """Remove only KOTAKLOVOL specifically"""
    print("\n🗑️ Removing KOTAKLOVOL (unavailable ETF)")
    print("=" * 40)
    
    data_manager = ETFDataManager()
    
    if "KOTAKLOVOL" not in data_manager.data["etfs"]:
        print("   💡 KOTAKLOVOL already removed")
        return False
    
    # Check for holdings
    active_holdings = [
        h for h in data_manager.data["portfolio"] 
        if h["etf_name"] == "KOTAKLOVOL" and h["status"] == "active"
    ]
    
    if active_holdings:
        print(f"   ⚠️ Found {len(active_holdings)} active holdings for KOTAKLOVOL")
        print("   💡 Consider selling these holdings before removal")
        return False
    
    # Remove KOTAKLOVOL
    del data_manager.data["etfs"]["KOTAKLOVOL"]
    data_manager._save_data()
    
    print("   ✅ KOTAKLOVOL successfully removed")
    return True

if __name__ == "__main__":
    print("🔧 ETF List Restoration")
    print("=" * 25)
    
    # Restore the renamed ETFs
    restore_renamed_etfs()
    
    # Remove only KOTAKLOVOL
    remove_only_kotaklovol()
    
    print("\n🎉 ETF list fixed!")
    print("💡 Now you have:")
    print("   ✅ Restored: ALPHA, IT, NV20, PSUBANK")
    print("   ❌ Removed: KOTAKLOVOL (unavailable)")
    print("\n📋 Next steps:")
    print("   1. Update price data for the restored ETFs")
    print("   2. Run enhanced_cli.py to verify the list")