#!/usr/bin/env python3
"""
Auto-update ETF names from Excel without user interaction
"""

from etf_symbol_updater import ETFSymbolUpdater
from etf_data_manager import ETFDataManager

def auto_update_names():
    print("🔄 Auto-Updating ETF Names from Excel")
    print("=" * 40)
    
    # Initialize
    data_manager = ETFDataManager()
    updater = ETFSymbolUpdater(data_manager)
    
    # Define the mappings detected from your Excel file
    name_mappings = {
        "KOTAKALPHA": "ALPHA",
        "KOTAKIT": "IT", 
        "KOTAKNV20": "NV20",
        "KOTAKPSUBK": "PSUBANK"
    }
    
    print("📋 ETF Name Updates to Perform:")
    for old_name, new_name in name_mappings.items():
        print(f"   {old_name} → {new_name}")
    
    # Create manual backup
    import shutil
    import datetime
    backup_file = f"etf_data_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    shutil.copy("etf_data.json", backup_file)
    print(f"\n📋 Backup created: {backup_file}")
    
    # Perform updates
    print(f"\n🔄 Executing Updates...")
    success_count = 0
    
    for old_name, new_name in name_mappings.items():
        print(f"\n   Updating {old_name} → {new_name}...")
        
        # Check if old ETF exists
        if old_name not in data_manager.data["etfs"]:
            print(f"   ⚠️ {old_name} not found in current data")
            continue
            
        # Check if new name already exists
        if new_name in data_manager.data["etfs"]:
            print(f"   ⚠️ {new_name} already exists, skipping...")
            continue
        
        # Perform the update
        try:
            updater.update_etf_data_with_new_symbol(old_name, new_name)
            success = True
        except Exception as e:
            print(f"   Error: {e}")
            success = False
        if success:
            print(f"   ✅ Successfully updated {old_name} → {new_name}")
            success_count += 1
        else:
            print(f"   ❌ Failed to update {old_name} → {new_name}")
    
    print(f"\n🎉 Update Complete!")
    print(f"   Successfully updated: {success_count}/{len(name_mappings)} ETFs")
    print(f"   Backup file: {backup_file}")
    
    # Show final status
    print(f"\n📊 Updated ETF Names:")
    for old_name, new_name in name_mappings.items():
        if new_name in data_manager.data["etfs"]:
            print(f"   ✅ {new_name} (was {old_name})")
        else:
            print(f"   ❌ {old_name} (update failed)")
    
    return success_count == len(name_mappings)

if __name__ == "__main__":
    success = auto_update_names()
    if success:
        print("\n🚀 All ETF names updated successfully!")
        print("💡 You can now run enhanced_cli.py with the new ETF names")
    else:
        print("\n⚠️ Some updates failed. Check the errors above.")