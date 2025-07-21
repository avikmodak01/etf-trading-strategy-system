#!/usr/bin/env python3
"""
ETF Symbol Updater - Handle ETF name changes and symbol updates
"""

import json
import pandas as pd
from datetime import datetime
from etf_data_manager import ETFDataManager
from typing import Dict, List, Tuple, Optional

class ETFSymbolUpdater:
    """Manages ETF symbol changes and name updates"""
    
    def __init__(self, data_manager: ETFDataManager):
        self.data_manager = data_manager
        self.symbol_mapping_file = "etf_symbol_mappings.json"
        self.load_symbol_mappings()
    
    def load_symbol_mappings(self):
        """Load existing symbol mappings"""
        try:
            with open(self.symbol_mapping_file, 'r') as f:
                self.symbol_mappings = json.load(f)
        except FileNotFoundError:
            # Create default mappings file
            self.symbol_mappings = {
                "mappings": {
                    "KOTAKGOLD": "GOLD1",  # Your recent change
                    # Add more mappings as needed
                },
                "last_updated": datetime.now().isoformat(),
                "version": "1.0"
            }
            self.save_symbol_mappings()
    
    def save_symbol_mappings(self):
        """Save symbol mappings to file"""
        self.symbol_mappings["last_updated"] = datetime.now().isoformat()
        with open(self.symbol_mapping_file, 'w') as f:
            json.dump(self.symbol_mappings, f, indent=2, default=str)
    
    def add_symbol_mapping(self, old_symbol: str, new_symbol: str, reason: str = ""):
        """Add a new symbol mapping"""
        print(f"📝 Adding symbol mapping: {old_symbol} → {new_symbol}")
        
        self.symbol_mappings["mappings"][old_symbol] = new_symbol
        
        # Add metadata
        if "mapping_history" not in self.symbol_mappings:
            self.symbol_mappings["mapping_history"] = []
        
        self.symbol_mappings["mapping_history"].append({
            "old_symbol": old_symbol,
            "new_symbol": new_symbol,
            "date": datetime.now().isoformat(),
            "reason": reason
        })
        
        self.save_symbol_mappings()
        print(f"✅ Symbol mapping saved: {old_symbol} → {new_symbol}")
    
    def update_etf_data_with_new_symbol(self, old_symbol: str, new_symbol: str):
        """Update ETF data when symbol changes"""
        print(f"\n🔄 Updating ETF data: {old_symbol} → {new_symbol}")
        
        # Check if old symbol exists in data
        if old_symbol not in self.data_manager.data["etfs"]:
            print(f"⚠️ Old symbol {old_symbol} not found in ETF data")
            return False
        
        # Get old data
        old_data = self.data_manager.data["etfs"][old_symbol].copy()
        
        # Update symbol name in the data
        old_data["name"] = new_symbol
        
        # Add new symbol with old data
        self.data_manager.data["etfs"][new_symbol] = old_data
        
        # Update portfolio holdings
        for holding in self.data_manager.data["portfolio"]:
            if holding["etf_name"] == old_symbol:
                holding["etf_name"] = new_symbol
                print(f"📊 Updated portfolio holding: {old_symbol} → {new_symbol}")
        
        # Update transactions
        for transaction in self.data_manager.data["transactions"]:
            if transaction["etf_name"] == old_symbol:
                transaction["etf_name"] = new_symbol
                print(f"💰 Updated transaction: {old_symbol} → {new_symbol}")
        
        # Remove old symbol
        del self.data_manager.data["etfs"][old_symbol]
        
        # Save updated data
        self.data_manager._save_data()
        
        print(f"✅ Successfully updated all data: {old_symbol} → {new_symbol}")
        return True
    
    def sync_with_excel_file(self, excel_file: str = "etf-list.xlsx"):
        """Sync with updated Excel file and detect changes"""
        print(f"\n📊 Syncing with {excel_file}...")
        
        try:
            # Load current Excel file
            df = pd.read_excel(excel_file)
            excel_symbols = set(df.iloc[:, 0].tolist())
            
            # Get current symbols in data
            current_symbols = set(self.data_manager.data["etfs"].keys())
            
            # Find differences
            new_symbols = excel_symbols - current_symbols
            removed_symbols = current_symbols - excel_symbols
            
            print(f"📈 Current symbols in data: {len(current_symbols)}")
            print(f"📋 Symbols in Excel: {len(excel_symbols)}")
            
            if new_symbols:
                print(f"\n🆕 New symbols found: {new_symbols}")
                for symbol in new_symbols:
                    self.data_manager.data["etfs"][symbol] = {
                        "name": symbol,
                        "cmp": None,
                        "dma_20": None,
                        "last_price_update": None,
                        "deviation_percent": None
                    }
                    print(f"   ✅ Added: {symbol}")
            
            if removed_symbols:
                print(f"\n🔄 Removed/renamed symbols: {removed_symbols}")
                for old_symbol in removed_symbols:
                    # Check if this is a known mapping
                    if old_symbol in self.symbol_mappings["mappings"]:
                        new_symbol = self.symbol_mappings["mappings"][old_symbol]
                        print(f"   📝 Known mapping: {old_symbol} → {new_symbol}")
                        self.update_etf_data_with_new_symbol(old_symbol, new_symbol)
                    else:
                        print(f"   ⚠️ Unknown removed symbol: {old_symbol}")
                        print(f"      This symbol was in data but not in Excel")
                        print(f"      You may need to add a mapping if it was renamed")
            
            # Save changes
            self.data_manager._save_data()
            
            print(f"\n✅ Sync completed!")
            return True
            
        except Exception as e:
            print(f"❌ Error syncing with Excel: {e}")
            return False
    
    def interactive_symbol_update(self):
        """Interactive tool to add symbol mappings"""
        print("\n🔧 Interactive ETF Symbol Update Tool")
        print("=" * 45)
        
        print("\nCurrent symbol mappings:")
        if self.symbol_mappings["mappings"]:
            for old, new in self.symbol_mappings["mappings"].items():
                print(f"   {old} → {new}")
        else:
            print("   No mappings found")
        
        while True:
            print("\nOptions:")
            print("1. Add new symbol mapping")
            print("2. Sync with Excel file")
            print("3. View current mappings")
            print("4. Exit")
            
            choice = input("\nEnter choice (1-4): ").strip()
            
            if choice == '1':
                old_symbol = input("Enter old symbol: ").strip().upper()
                new_symbol = input("Enter new symbol: ").strip().upper()
                reason = input("Enter reason (optional): ").strip()
                
                self.add_symbol_mapping(old_symbol, new_symbol, reason)
                
                # Ask if user wants to update data immediately
                update_now = input(f"Update ETF data now? (y/n): ").strip().lower()
                if update_now == 'y':
                    self.update_etf_data_with_new_symbol(old_symbol, new_symbol)
            
            elif choice == '2':
                excel_file = input("Enter Excel file path (default: etf-list.xlsx): ").strip()
                if not excel_file:
                    excel_file = "etf-list.xlsx"
                self.sync_with_excel_file(excel_file)
            
            elif choice == '3':
                print("\n📋 Current Symbol Mappings:")
                print("-" * 30)
                for old, new in self.symbol_mappings["mappings"].items():
                    print(f"   {old} → {new}")
                
                if "mapping_history" in self.symbol_mappings:
                    print("\n📅 Mapping History:")
                    print("-" * 20)
                    for record in self.symbol_mappings["mapping_history"]:
                        date_str = record["date"][:10]
                        print(f"   {date_str}: {record['old_symbol']} → {record['new_symbol']}")
                        if record.get("reason"):
                            print(f"              Reason: {record['reason']}")
            
            elif choice == '4':
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice")
    
    def bulk_update_from_mapping_file(self, mapping_file: str):
        """Update multiple symbols from a CSV mapping file"""
        print(f"\n📁 Bulk update from {mapping_file}")
        
        try:
            # Expected format: old_symbol,new_symbol,reason
            df = pd.read_csv(mapping_file)
            
            for _, row in df.iterrows():
                old_symbol = str(row['old_symbol']).strip().upper()
                new_symbol = str(row['new_symbol']).strip().upper()
                reason = str(row.get('reason', '')).strip()
                
                print(f"\n🔄 Processing: {old_symbol} → {new_symbol}")
                
                # Add mapping
                self.add_symbol_mapping(old_symbol, new_symbol, reason)
                
                # Update data
                self.update_etf_data_with_new_symbol(old_symbol, new_symbol)
            
            print(f"\n✅ Bulk update completed!")
            
        except Exception as e:
            print(f"❌ Error in bulk update: {e}")
    
    def validate_symbols_with_yahoo(self, symbols: List[str] = None):
        """Validate ETF symbols with Yahoo Finance"""
        print("\n🔍 Validating ETF symbols with Yahoo Finance...")
        
        if symbols is None:
            symbols = list(self.data_manager.data["etfs"].keys())
        
        from price_fetcher import PriceFetcher
        fetcher = PriceFetcher()
        
        valid_symbols = []
        invalid_symbols = []
        
        for symbol in symbols:
            print(f"   Testing {symbol}...", end="")
            try:
                data = fetcher.fetch_yahoo_finance_data(symbol)
                if data and data.get('current_price'):
                    valid_symbols.append(symbol)
                    print(" ✅")
                else:
                    invalid_symbols.append(symbol)
                    print(" ❌")
            except Exception as e:
                invalid_symbols.append(symbol)
                print(f" ❌ ({str(e)[:30]})")
        
        print(f"\n📊 Validation Results:")
        print(f"   ✅ Valid symbols: {len(valid_symbols)}")
        print(f"   ❌ Invalid symbols: {len(invalid_symbols)}")
        
        if invalid_symbols:
            print(f"\n⚠️ Invalid symbols that may need updating:")
            for symbol in invalid_symbols:
                print(f"   - {symbol}")
        
        return valid_symbols, invalid_symbols


def main():
    """Main function for command-line usage"""
    print("🔧 ETF Symbol Update Tool")
    print("=" * 30)
    
    # Initialize
    data_manager = ETFDataManager()
    updater = ETFSymbolUpdater(data_manager)
    
    # Run interactive tool
    updater.interactive_symbol_update()


if __name__ == "__main__":
    main()