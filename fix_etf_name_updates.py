#!/usr/bin/env python3
"""
Fix ETF name updates - transfer data from old names to new names and remove old entries
"""

import json
import shutil
from datetime import datetime
from etf_data_manager import ETFDataManager

def fix_etf_name_updates():
    print("🔧 Fixing ETF Name Updates")
    print("=" * 30)
    
    # Initialize
    data_manager = ETFDataManager()
    
    # Define the mappings
    name_mappings = {
        "KOTAKALPHA": "ALPHA",
        "KOTAKIT": "IT", 
        "KOTAKNV20": "NV20",
        "KOTAKPSUBK": "PSUBANK"
    }
    
    # Create backup
    backup_file = f"etf_data_backup_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    shutil.copy("etf_data.json", backup_file)
    print(f"📋 Backup created: {backup_file}")
    
    print(f"\n🔄 Processing ETF name transfers...")
    
    for old_name, new_name in name_mappings.items():
        print(f"\n   Processing {old_name} → {new_name}...")
        
        # Check if both exist
        old_exists = old_name in data_manager.data["etfs"]
        new_exists = new_name in data_manager.data["etfs"]
        
        print(f"   Old ETF '{old_name}' exists: {old_exists}")
        print(f"   New ETF '{new_name}' exists: {new_exists}")
        
        if old_exists and new_exists:
            # Transfer data from old to new
            old_data = data_manager.data["etfs"][old_name]
            new_data = data_manager.data["etfs"][new_name]
            
            # If old has data and new doesn't, transfer it
            if old_data.get("cmp") is not None and new_data.get("cmp") is None:
                print(f"   📊 Transferring price data from {old_name} to {new_name}")
                data_manager.data["etfs"][new_name].update({
                    "cmp": old_data.get("cmp"),
                    "dma_20": old_data.get("dma_20"),
                    "last_price_update": old_data.get("last_price_update"),
                    "deviation_percent": old_data.get("deviation_percent"),
                    "volume_data": old_data.get("volume_data"),
                    "volume_qualified": old_data.get("volume_qualified"),
                    "volume_last_check": old_data.get("volume_last_check")
                })
            
            # Update portfolio holdings
            portfolio_updated = 0
            for holding in data_manager.data["portfolio"]:
                if holding["etf_name"] == old_name:
                    holding["etf_name"] = new_name
                    portfolio_updated += 1
            
            # Update transactions
            transactions_updated = 0
            for transaction in data_manager.data["transactions"]:
                if transaction["etf_name"] == old_name:
                    transaction["etf_name"] = new_name
                    transactions_updated += 1
            
            print(f"   📈 Updated {portfolio_updated} portfolio holdings")
            print(f"   📊 Updated {transactions_updated} transactions")
            
            # Remove old ETF entry
            del data_manager.data["etfs"][old_name]
            print(f"   🗑️ Removed old ETF entry: {old_name}")
            
        elif old_exists and not new_exists:
            # Simply rename
            print(f"   🔄 Renaming {old_name} to {new_name}")
            data_manager.data["etfs"][new_name] = data_manager.data["etfs"][old_name]
            data_manager.data["etfs"][new_name]["name"] = new_name
            del data_manager.data["etfs"][old_name]
            
            # Update portfolio and transactions
            for holding in data_manager.data["portfolio"]:
                if holding["etf_name"] == old_name:
                    holding["etf_name"] = new_name
            
            for transaction in data_manager.data["transactions"]:
                if transaction["etf_name"] == old_name:
                    transaction["etf_name"] = new_name
            
        elif not old_exists and new_exists:
            print(f"   ✅ {new_name} already properly configured")
            
        else:
            print(f"   ⚠️ Neither {old_name} nor {new_name} exists")
    
    # Save updated data
    data_manager._save_data()
    
    print(f"\n🎉 ETF Name Fix Complete!")
    
    # Show final status
    print(f"\n📊 Final ETF Status:")
    for old_name, new_name in name_mappings.items():
        old_exists = old_name in data_manager.data["etfs"]
        new_exists = new_name in data_manager.data["etfs"]
        
        if new_exists and not old_exists:
            print(f"   ✅ {new_name} (properly renamed from {old_name})")
        elif old_exists:
            print(f"   ⚠️ {old_name} still exists (not renamed)")
        else:
            print(f"   ❓ {new_name} status unclear")
    
    return True

if __name__ == "__main__":
    success = fix_etf_name_updates()
    if success:
        print("\n🚀 ETF names successfully fixed!")
        print("💡 Your system now uses the updated ETF names")
    else:
        print("\n⚠️ Fix incomplete. Check errors above.")