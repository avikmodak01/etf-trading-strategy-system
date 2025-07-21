#!/usr/bin/env python3
"""
Quick ETF Name Sync Script
Automatically sync ETF names from Excel file
"""

import sys
from etf_symbol_updater import ETFSymbolUpdater
from etf_data_manager import ETFDataManager

def auto_sync_from_excel():
    print("🔄 Auto-Syncing ETF Names from Excel File")
    print("=" * 45)
    
    try:
        # Initialize components
        data_manager = ETFDataManager()
        updater = ETFSymbolUpdater(data_manager)
        
        print("📊 Loading current ETF data...")
        current_etfs = set(data_manager.data["etfs"].keys())
        print(f"   Current ETFs in system: {len(current_etfs)}")
        
        print("📋 Loading ETF names from Excel...")
        try:
            excel_etfs = data_manager.load_etf_list_from_excel("etf-list.xlsx")
            excel_etf_set = set(excel_etfs)
            print(f"   ETFs in Excel file: {len(excel_etfs)}")
        except Exception as e:
            print(f"❌ Error loading Excel file: {e}")
            print("💡 Make sure 'etf-list.xlsx' exists and has ETF names in the first column")
            return False
        
        print("\n🔍 Detecting Changes...")
        
        # Find differences
        only_in_current = current_etfs - excel_etf_set
        only_in_excel = excel_etf_set - current_etfs
        common_etfs = current_etfs & excel_etf_set
        
        print(f"   ETFs in both: {len(common_etfs)}")
        print(f"   Only in current system: {len(only_in_current)}")
        print(f"   Only in Excel (new/renamed): {len(only_in_excel)}")
        
        if only_in_current:
            print(f"\n📤 ETFs to be removed/renamed:")
            for etf in sorted(only_in_current):
                print(f"   - {etf}")
        
        if only_in_excel:
            print(f"\n📥 New ETFs in Excel:")
            for etf in sorted(only_in_excel):
                print(f"   + {etf}")
        
        # Detect potential renames (when counts are similar)
        if len(only_in_current) > 0 and len(only_in_excel) > 0:
            print(f"\n🔄 Potential ETF Name Changes Detected!")
            print(f"   This could be ETF renames: {len(only_in_current)} old → {len(only_in_excel)} new")
            
            old_etfs = sorted(only_in_current)
            new_etfs = sorted(only_in_excel)
            
            print(f"\n🤔 Possible mappings:")
            for i, old_etf in enumerate(old_etfs):
                if i < len(new_etfs):
                    new_etf = new_etfs[i]
                    print(f"   {old_etf} → {new_etf}?")
                else:
                    print(f"   {old_etf} → [to be removed]")
            
            print(f"\n❓ Do you want to proceed with automatic name updates?")
            print(f"   This will:")
            for i, old_etf in enumerate(old_etfs):
                if i < len(new_etfs):
                    new_etf = new_etfs[i]
                    print(f"   • Rename {old_etf} to {new_etf}")
                    print(f"     - Preserve all price data and volume info")
                    print(f"     - Update portfolio holdings")
                    print(f"     - Update transaction history")
                else:
                    print(f"   • Remove {old_etf} (no new name found)")
            
            # Get user confirmation
            confirm = input(f"\n✅ Proceed with these changes? (y/n): ").lower().strip()
            
            if confirm == 'y':
                print(f"\n🔄 Executing ETF name updates...")
                
                # Create backup first
                backup_file = updater.create_backup()
                print(f"📋 Backup created: {backup_file}")
                
                # Perform updates
                success_count = 0
                for i, old_etf in enumerate(old_etfs):
                    if i < len(new_etfs):
                        new_etf = new_etfs[i]
                        print(f"\n   Updating {old_etf} → {new_etf}...")
                        
                        success = updater.update_etf_symbol(old_etf, new_etf)
                        if success:
                            print(f"   ✅ Successfully updated {old_etf} → {new_etf}")
                            success_count += 1
                        else:
                            print(f"   ❌ Failed to update {old_etf} → {new_etf}")
                
                # Add any completely new ETFs
                for etf in only_in_excel:
                    if etf not in new_etfs[:len(old_etfs)]:  # Not part of renames
                        print(f"\n   Adding new ETF: {etf}")
                        data_manager.add_etf(etf, 0, 0)  # Add with zero prices
                        success_count += 1
                
                print(f"\n🎉 Update Complete!")
                print(f"   Successfully updated: {success_count} ETFs")
                print(f"   Backup file: {backup_file}")
                
                return True
                
            else:
                print("❌ Update cancelled by user")
                return False
        
        elif len(only_in_excel) > 0:
            # Only new ETFs, no renames
            print(f"\n➕ Adding {len(only_in_excel)} new ETFs...")
            for etf in only_in_excel:
                data_manager.add_etf(etf, 0, 0)
                print(f"   + Added {etf}")
            
            print(f"✅ Added {len(only_in_excel)} new ETFs")
            return True
            
        else:
            print("✅ No changes needed - Excel and system are in sync!")
            return True
    
    except Exception as e:
        print(f"❌ Error during sync: {e}")
        return False

if __name__ == "__main__":
    success = auto_sync_from_excel()
    if success:
        print("\n🚀 ETF names successfully synced!")
        print("💡 You can now run enhanced_cli.py with updated ETF names")
    else:
        print("\n⚠️ Sync incomplete. Please check errors above.")
        sys.exit(1)