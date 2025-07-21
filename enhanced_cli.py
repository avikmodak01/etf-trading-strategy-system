#!/usr/bin/env python3
"""
Enhanced Command Line Interface with Live Price Fetching
"""

import sys
from etf_data_manager import ETFDataManager
from trading_strategy import ETFTradingStrategy
from price_fetcher import PriceFetcher, PriceUpdateScheduler
from volume_filter import VolumeFilter
from investment_manager import InvestmentManager
import json
from datetime import datetime, timedelta

class EnhancedETFCLI:
    def __init__(self):
        self.data_manager = ETFDataManager()
        self.price_fetcher = PriceFetcher()
        self.volume_filter = VolumeFilter(self.data_manager, self.price_fetcher)
        self.investment_manager = InvestmentManager(self.data_manager)
        self.strategy = ETFTradingStrategy(self.data_manager, self.volume_filter)
        self.scheduler = PriceUpdateScheduler(self.data_manager, self.price_fetcher)
        
        # Load ETF list on startup
        try:
            self.data_manager.load_etf_list_from_excel("etf-list.xlsx")
            print("✅ ETF list loaded successfully")
        except Exception as e:
            print(f"❌ Error loading ETF list: {e}")
    
    def display_menu(self):
        """Display enhanced main menu"""
        print("\n" + "="*60)
        print("🤖 Enhanced ETF Trading Strategy System")
        print("="*60)
        print("📊 STRATEGY & PORTFOLIO")
        print("1. Get Daily Strategy Recommendations")
        print("2. View Portfolio & Holdings")
        print("3. Execute Buy Transaction")
        print("4. Execute Sell Transaction")
        print("5. View Trading Statistics")
        print()
        print("💰 PRICE DATA & UPDATES")
        print("6. Fetch Live Prices (Yahoo Finance)")
        print("7. Update Specific ETF Price")
        print("8. Update All ETF Prices")
        print("9. Import Prices from CSV")
        print("10. View Historical Data")
        print()
        print("🏆 ANALYSIS & RANKINGS")
        print("11. View ETF Rankings")
        print("12. Analyze ETF Performance")
        print("13. Get ETF Information")
        print()
        print("📊 VOLUME FILTERING")
        print("14. Update ETF Volume Status")
        print("15. View Volume Report")
        print("16. Set Volume Threshold")
        print("17. Toggle Volume Filtering")
        print()
        print("⚙️  TOOLS & SETTINGS")
        print("18. Load Sample Data")
        print("19. Export Portfolio Data")
        print("20. Schedule Auto Updates")
        print("21. Configure Investment Capital")
        print("22. ❌ Exit")
        print("="*60)
    
    def fetch_live_prices(self):
        """Fetch live prices for selected ETFs"""
        print("\n💰 Fetch Live ETF Prices")
        print("-" * 35)
        
        # Show available ETFs
        etf_list = list(self.data_manager.data["etfs"].keys())
        if not etf_list:
            print("❌ No ETFs found. Please load ETF list first.")
            return
        
        print("Available ETFs:")
        for i, etf in enumerate(etf_list, 1):
            print(f"{i:2d}. {etf}")
        
        print("\nOptions:")
        print("A. Fetch ALL ETF prices")
        print("S. Select specific ETFs (comma-separated numbers)")
        print("C. Cancel")
        
        choice = input("\nEnter your choice: ").strip().upper()
        
        if choice == 'C':
            return
        elif choice == 'A':
            selected_etfs = etf_list
        elif choice == 'S':
            try:
                numbers = [int(x.strip()) for x in input("Enter ETF numbers (e.g., 1,3,5): ").split(',')]
                selected_etfs = [etf_list[i-1] for i in numbers if 1 <= i <= len(etf_list)]
            except (ValueError, IndexError):
                print("❌ Invalid selection")
                return
        else:
            print("❌ Invalid choice")
            return
        
        if not selected_etfs:
            print("❌ No ETFs selected")
            return
        
        print(f"\n🔄 Fetching live prices for {len(selected_etfs)} ETFs...")
        
        # Fetch prices
        price_data = self.price_fetcher.fetch_multiple_etfs(selected_etfs, source="yahoo")
        
        updated_count = 0
        failed_count = 0
        
        print(f"\n{'ETF':<12}{'Current Price':<15}{'20-day MA':<12}{'Volume':<12}{'Change %'}")
        print("-" * 65)
        
        for etf in selected_etfs:
            if etf in price_data and price_data[etf]:
                data = price_data[etf]
                
                # Update in data manager
                if data.get('current_price') and data.get('ma_20'):
                    self.data_manager.update_etf_price(
                        etf, 
                        data['current_price'], 
                        data['ma_20']
                    )
                    updated_count += 1
                    
                    print(f"{etf:<12}₹{data['current_price']:<14.2f}₹{data['ma_20']:<11.2f}{data.get('volume', 0):<12,}{data.get('change_percent', 0):>7.2f}%")
                else:
                    print(f"{etf:<12}{'Incomplete data':<50}")
                    failed_count += 1
            else:
                print(f"{etf:<12}{'Failed to fetch':<50}")
                failed_count += 1
        
        print(f"\n✅ Successfully updated: {updated_count}")
        if failed_count > 0:
            print(f"❌ Failed to update: {failed_count}")
    
    def update_specific_etf(self):
        """Update a specific ETF price manually or via API"""
        print("\n💰 Update Specific ETF Price")
        print("-" * 35)
        
        etf_name = input("Enter ETF name: ").strip().upper()
        
        print("\nOptions:")
        print("1. Fetch live price from Yahoo Finance")
        print("2. Enter price manually")
        
        choice = input("Choose option (1-2): ").strip()
        
        if choice == '1':
            # Fetch from Yahoo Finance
            data = self.price_fetcher.fetch_yahoo_finance_data(etf_name)
            if data and data.get('current_price') and data.get('ma_20'):
                self.data_manager.update_etf_price(
                    etf_name,
                    data['current_price'],
                    data['ma_20']
                )
                print(f"✅ Updated {etf_name}:")
                print(f"   Current Price: ₹{data['current_price']:.2f}")
                print(f"   20-day MA: ₹{data['ma_20']:.2f}")
                print(f"   Volume: {data.get('volume', 0):,}")
                print(f"   Change: {data.get('change_percent', 0):.2f}%")
            else:
                print(f"❌ Failed to fetch data for {etf_name}")
        
        elif choice == '2':
            # Manual entry
            try:
                cmp = float(input(f"Enter current market price for {etf_name}: "))
                dma_20 = float(input(f"Enter 20-day moving average for {etf_name}: "))
                
                self.data_manager.update_etf_price(etf_name, cmp, dma_20)
                print(f"✅ Updated {etf_name}: CMP=₹{cmp:.2f}, 20DMA=₹{dma_20:.2f}")
                
            except ValueError:
                print("❌ Invalid price format")
        else:
            print("❌ Invalid choice")
    
    def update_all_etf_prices(self):
        """Update all ETF prices automatically"""
        print("\n🔄 Updating All ETF Prices")
        print("-" * 35)
        
        etf_list = list(self.data_manager.data["etfs"].keys())
        if not etf_list:
            print("❌ No ETFs found to update")
            return
        
        print(f"Found {len(etf_list)} ETFs to update...")
        confirm = input("Proceed with automatic update? (y/n): ").lower()
        
        if confirm != 'y':
            print("Update cancelled")
            return
        
        updated_count = self.scheduler.update_all_etf_prices(etf_list)
        
        if updated_count > 0:
            print(f"\n🎉 Successfully updated {updated_count} ETFs!")
            print("You can now view updated rankings and get strategy recommendations.")
        else:
            print("❌ No ETFs were updated successfully")
    
    def import_prices_from_csv(self):
        """Import ETF prices from CSV file"""
        print("\n📁 Import Prices from CSV")
        print("-" * 30)
        
        csv_file = input("Enter CSV file path: ").strip()
        
        print("\nCSV Column Configuration:")
        symbol_col = input("Symbol column name (default: 'Symbol'): ").strip() or "Symbol"
        price_col = input("Price column name (default: 'LTP'): ").strip() or "LTP"
        volume_col = input("Volume column name (default: 'Volume'): ").strip() or "Volume"
        
        try:
            price_data = self.price_fetcher.import_from_csv(csv_file, symbol_col, price_col, volume_col)
            
            if price_data:
                updated_count = 0
                for symbol, data in price_data.items():
                    if data.get('current_price') and data.get('ma_20'):
                        self.data_manager.update_etf_price(
                            symbol,
                            data['current_price'],
                            data['ma_20']
                        )
                        updated_count += 1
                        print(f"✅ Updated {symbol}: ₹{data['current_price']:.2f}")
                
                print(f"\n🎉 Successfully imported {updated_count} ETFs from CSV!")
            else:
                print("❌ No data imported from CSV")
                
        except FileNotFoundError:
            print(f"❌ File not found: {csv_file}")
        except Exception as e:
            print(f"❌ Error importing CSV: {e}")
    
    def view_historical_data(self):
        """View historical price data for an ETF"""
        print("\n📈 View Historical Data")
        print("-" * 25)
        
        etf_name = input("Enter ETF name: ").strip().upper()
        days = input("Enter number of days (default: 30): ").strip()
        days = int(days) if days.isdigit() else 30
        
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            hist_data = self.price_fetcher.fetch_historical_data(
                etf_name,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            
            if hist_data is not None and not hist_data.empty:
                print(f"\n📊 {etf_name} - Last {days} days:")
                print("-" * 60)
                print(f"{'Date':<12}{'Close':<10}{'Volume':<12}{'MA20':<10}{'MA50':<10}")
                print("-" * 60)
                
                # Show last 10 days
                recent_data = hist_data.tail(10)
                for date, row in recent_data.iterrows():
                    date_str = date.strftime('%Y-%m-%d')
                    close_price = row['Close']
                    volume = int(row['Volume']) if not pd.isna(row['Volume']) else 0
                    ma20 = row.get('MA_20', 0)
                    ma50 = row.get('MA_50', 0)
                    
                    print(f"{date_str:<12}₹{close_price:<9.2f}{volume:<12,}₹{ma20:<9.2f}₹{ma50:<9.2f}")
                
                # Summary
                print("-" * 60)
                current_price = hist_data['Close'].iloc[-1]
                ma20_current = hist_data['MA_20'].iloc[-1]
                high_52w = hist_data['High'].max()
                low_52w = hist_data['Low'].min()
                
                print(f"Current Price: ₹{current_price:.2f}")
                print(f"20-day MA: ₹{ma20_current:.2f}")
                print(f"Deviation from MA: {((current_price - ma20_current) / ma20_current * 100):.2f}%")
                print(f"52W High: ₹{high_52w:.2f}")
                print(f"52W Low: ₹{low_52w:.2f}")
                
            else:
                print(f"❌ No historical data found for {etf_name}")
                
        except Exception as e:
            print(f"❌ Error fetching historical data: {e}")
    
    def analyze_etf_performance(self):
        """Analyze ETF performance and trends"""
        print("\n📊 ETF Performance Analysis")
        print("-" * 35)
        
        rankings = self.data_manager.get_etf_rankings()
        if not rankings:
            print("❌ No ETF data available. Please update prices first.")
            return
        
        print("📈 TOP PERFORMERS (Least deviation from 20-day MA):")
        print(f"{'Rank':<6}{'ETF':<12}{'Current':<10}{'20DMA':<10}{'Deviation':<12}{'Status'}")
        print("-" * 65)
        
        holdings = set(self.data_manager.get_current_holdings().keys())
        
        for i, (etf_name, cmp, dma_20, deviation) in enumerate(rankings[:10], 1):
            status = "HELD" if etf_name in holdings else "NEW"
            deviation_color = "🔴" if deviation > 0 else "🟢"
            
            print(f"{i:<6}{etf_name:<12}₹{cmp:<9.2f}₹{dma_20:<9.2f}{deviation_color}{deviation:<10.2f}%{status}")
        
        # Analysis summary
        positive_deviation = [r for r in rankings if r[3] > 0]
        negative_deviation = [r for r in rankings if r[3] < 0]
        
        print(f"\n📋 MARKET ANALYSIS:")
        print(f"   Total ETFs analyzed: {len(rankings)}")
        print(f"   Above 20-day MA: {len(positive_deviation)} ({len(positive_deviation)/len(rankings)*100:.1f}%)")
        print(f"   Below 20-day MA: {len(negative_deviation)} ({len(negative_deviation)/len(rankings)*100:.1f}%)")
        
        if negative_deviation:
            best_opportunity = negative_deviation[0]
            print(f"   Best opportunity: {best_opportunity[0]} ({best_opportunity[3]:.2f}% below MA)")
    
    def get_etf_information(self):
        """Get detailed ETF information"""
        print("\n📋 ETF Information")
        print("-" * 20)
        
        etf_name = input("Enter ETF name: ").strip().upper()
        
        try:
            info = self.price_fetcher.get_etf_info(etf_name)
            
            if info:
                print(f"\n📊 {info['symbol']} - {info['name']}")
                print("-" * 50)
                print(f"Category: {info['category']}")
                print(f"Sector: {info['sector']}")
                print(f"Expense Ratio: {info['expense_ratio']}")
                print(f"Net Assets: {info['net_assets']}")
                print(f"Inception Date: {info['inception_date']}")
                
                # Get current data if available
                if etf_name in self.data_manager.data["etfs"]:
                    etf_data = self.data_manager.data["etfs"][etf_name]
                    if etf_data.get('cmp'):
                        print(f"\nCurrent Market Data:")
                        print(f"Current Price: ₹{etf_data['cmp']:.2f}")
                        print(f"20-day MA: ₹{etf_data['dma_20']:.2f}")
                        print(f"Deviation: {etf_data['deviation_percent']:.2f}%")
                        print(f"Last Updated: {etf_data['last_price_update']}")
            else:
                print(f"❌ Could not fetch information for {etf_name}")
                
        except Exception as e:
            print(f"❌ Error fetching ETF information: {e}")
    
    def export_portfolio_data(self):
        """Export portfolio data to CSV"""
        print("\n📤 Export Portfolio Data")
        print("-" * 25)
        
        try:
            import pandas as pd
            
            # Export holdings
            portfolio = self.data_manager.get_portfolio_summary()
            
            if portfolio['holdings_detail']:
                df_holdings = pd.DataFrame(portfolio['holdings_detail'])
                
                filename = f"portfolio_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                df_holdings.to_csv(filename, index=False)
                
                print(f"✅ Portfolio exported to: {filename}")
                print(f"   Total ETFs: {len(df_holdings)}")
                print(f"   Total Value: ₹{portfolio['current_value']:,.2f}")
            else:
                print("❌ No portfolio data to export")
                
        except ImportError:
            print("❌ Pandas not available for CSV export")
        except Exception as e:
            print(f"❌ Error exporting data: {e}")
    
    def schedule_auto_updates(self):
        """Configure automatic price updates"""
        print("\n⏰ Schedule Automatic Updates")
        print("-" * 35)
        
        print("This feature allows automatic price updates during market hours.")
        print("Updates will occur at:")
        print("   - 9:35 AM (Market open)")
        print("   - 12:00 PM (Mid-day)")
        print("   - 3:25 PM (Market close)")
        print("   - Monday to Friday only")
        
        confirm = input("\nStart automatic updates? (y/n): ").lower()
        
        if confirm == 'y':
            print("🔄 Starting automatic update scheduler...")
            print("Press Ctrl+C to stop the scheduler")
            
            try:
                self.scheduler.schedule_regular_updates()
            except KeyboardInterrupt:
                print("\n⏹️  Scheduler stopped by user")
        else:
            print("Automatic updates not started")
    
    def configure_investment_capital(self):
        """Configure investment capital and strategies"""
        print("\n💰 Investment Capital Configuration")
        print("-" * 40)
        self.investment_manager.interactive_investment_setup()
    
    def run(self):
        """Run the enhanced command line interface"""
        print("🤖 Enhanced ETF Trading Strategy System")
        print("Welcome! This system includes live price fetching capabilities.")
        
        while True:
            try:
                self.display_menu()
                choice = input("\nEnter your choice (1-22): ").strip()
                
                if choice == '1':
                    recommendations = self.get_daily_strategy()
                elif choice == '2':
                    self.view_portfolio()
                elif choice == '3':
                    self.execute_buy_transaction()
                elif choice == '4':
                    self.execute_sell_transaction()
                elif choice == '5':
                    self.view_statistics()
                elif choice == '6':
                    self.fetch_live_prices()
                elif choice == '7':
                    self.update_specific_etf()
                elif choice == '8':
                    self.update_all_etf_prices()
                elif choice == '9':
                    self.import_prices_from_csv()
                elif choice == '10':
                    self.view_historical_data()
                elif choice == '11':
                    self.view_rankings()
                elif choice == '12':
                    self.analyze_etf_performance()
                elif choice == '13':
                    self.get_etf_information()
                elif choice == '14':
                    self.update_etf_volume_status()
                elif choice == '15':
                    self.view_volume_report()
                elif choice == '16':
                    self.set_volume_threshold()
                elif choice == '17':
                    self.toggle_volume_filtering()
                elif choice == '18':
                    self.load_sample_data()
                elif choice == '19':
                    self.export_portfolio_data()
                elif choice == '20':
                    self.schedule_auto_updates()
                elif choice == '21':
                    self.configure_investment_capital()
                elif choice == '22':
                    print("\n👋 Thank you for using Enhanced ETF Trading Strategy System!")
                    break
                else:
                    print("❌ Invalid choice. Please enter a number between 1-22.")
                
                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {e}")
                input("Press Enter to continue...")
    
    # Include methods from original CLI
    def get_daily_strategy(self):
        """Display daily trading recommendations"""
        print("\n📊 Daily Strategy Recommendations")
        print("-" * 40)
        
        recommendations = self.strategy.get_daily_recommendations()
        
        # Buy recommendation
        buy_rec = recommendations['buy_recommendation']
        print("\n🟢 BUY RECOMMENDATION:")
        if buy_rec['action'] != 'no_action':
            print(f"   ETF: {buy_rec['etf_name']}")
            print(f"   Action: {buy_rec['action'].replace('_', ' ').title()}")
            current_price = buy_rec.get('cmp', buy_rec.get('current_price', 'N/A'))
            print(f"   Current Price: ₹{current_price}")
            if 'deviation_percent' in buy_rec:
                print(f"   Deviation: {buy_rec['deviation_percent']:.2f}%")
            print(f"   Reason: {buy_rec['reason']}")
        else:
            print(f"   No action recommended")
            print(f"   Reason: {buy_rec['reason']}")
        
        # Sell recommendation
        sell_rec = recommendations['sell_recommendation']
        print("\n🔴 SELL RECOMMENDATION:")
        if sell_rec['action'] != 'no_action':
            print(f"   ETF: {sell_rec['etf_name']}")
            print(f"   Current Price: ₹{sell_rec['current_price']}")
            print(f"   Profit: {sell_rec['profit_percent']:.2f}%")
            print(f"   Reason: {sell_rec['reason']}")
        else:
            print(f"   No action recommended")
            print(f"   Reason: {sell_rec['reason']}")
        
        # Portfolio summary
        portfolio = recommendations['portfolio_summary']
        print(f"\n📊 PORTFOLIO SUMMARY:")
        print(f"   Total ETFs: {portfolio['total_etfs']}")
        print(f"   Total Investment: ₹{portfolio['total_investments']:,.2f}")
        print(f"   Current Value: ₹{portfolio['current_value']:,.2f}")
        print(f"   P&L: ₹{portfolio['total_profit_loss']:,.2f}")
        
        return recommendations
    
    # Include other methods from original CLI...
    def view_portfolio(self):
        """Display current portfolio"""
        print("\n📈 Current Portfolio")
        print("-" * 30)
        
        portfolio = self.data_manager.get_portfolio_summary()
        
        print(f"Total ETFs: {portfolio['total_etfs']}")
        print(f"Total Investment: ₹{portfolio['total_investments']:,.2f}")
        print(f"Current Value: ₹{portfolio['current_value']:,.2f}")
        print(f"P&L: ₹{portfolio['total_profit_loss']:,.2f}")
        
        if portfolio['holdings_detail']:
            print("\nHoldings Detail:")
            print("-" * 60)
            for holding in portfolio['holdings_detail']:
                print(f"\n🔸 {holding['etf_name']}")
                print(f"   Quantity: {holding['quantity']}")
                print(f"   Avg Buy Price: ₹{holding['avg_buy_price']}")
                print(f"   Current Price: ₹{holding['current_price']}")
                print(f"   Total Cost: ₹{holding['total_cost']:,.2f}")
                print(f"   Current Value: ₹{holding['current_value']:,.2f}")
                print(f"   P&L: ₹{holding['profit_loss']:,.2f} ({holding['profit_loss_percent']:.2f}%)")
        else:
            print("\nNo current holdings.")
    
    def view_rankings(self):
        """Display ETF rankings"""
        print("\n🏆 ETF Rankings")
        print("-" * 40)
        
        rankings = self.data_manager.get_etf_rankings()
        
        if rankings:
            print("Ranked by deviation from 20-day moving average:")
            print(f"{'Rank':<6}{'ETF':<12}{'CMP':<10}{'20DMA':<10}{'Deviation'}")
            print("-" * 50)
            
            for i, (etf_name, cmp, dma_20, deviation) in enumerate(rankings[:20], 1):
                print(f"{i:<6}{etf_name:<12}₹{cmp:<9.2f}₹{dma_20:<9.2f}{deviation:>8.2f}%")
        else:
            print("No ETF data available. Please update prices first.")
    
    def execute_buy_transaction(self):
        """Execute a buy transaction with investment amount calculation"""
        print("\n💸 Execute Buy Transaction")
        print("-" * 35)
        
        # Get current recommendation
        recommendations = self.strategy.get_daily_recommendations()
        buy_rec = recommendations['buy_recommendation']
        
        if buy_rec['action'] == 'no_action':
            print("❌ No buy recommendation available today.")
            print(f"Reason: {buy_rec['reason']}")
            return
        
        print(f"Recommended ETF: {buy_rec['etf_name']}")
        print(f"Action: {buy_rec['action'].replace('_', ' ').title()}")
        current_price = buy_rec.get('cmp', buy_rec.get('current_price', 0))
        print(f"Current Price: ₹{current_price:.2f}")
        print(f"Reason: {buy_rec['reason']}")
        
        try:
            # Step 1: Ask for investment amount
            default_investment = self.investment_manager.config["default_investment_per_trade"]
            print(f"\n💰 Investment Amount (Default: ₹{default_investment:,})")
            investment_input = input(f"Enter investment amount (or press Enter for ₹{default_investment:,}): ").strip()
            
            if investment_input:
                investment_amount = float(investment_input)
            else:
                investment_amount = default_investment
            
            # Step 2: Get investment suggestion
            suggestion = self.investment_manager.get_investment_suggestion(
                buy_rec['etf_name'], current_price, investment_amount
            )
            
            # Display investment suggestion
            self.investment_manager.display_investment_suggestion(suggestion)
            
            # Step 3: Ask for actual quantity
            suggested_qty = suggestion['suggested_quantity']
            print(f"\n📊 Quantity Selection:")
            quantity_input = input(f"Enter actual quantity to buy (suggested: {suggested_qty}): ").strip()
            
            if quantity_input:
                quantity = int(quantity_input)
            else:
                quantity = suggested_qty
            
            # Step 4: Ask for actual price
            actual_price = float(input(f"Enter actual purchase price (current: ₹{current_price:.2f}): "))
            
            # Validate inputs
            is_valid, validation_msg = self.strategy.validate_transaction_inputs(quantity, actual_price)
            if not is_valid:
                print(f"❌ {validation_msg}")
                return
            
            # Step 5: Final confirmation
            total_amount = quantity * actual_price
            print(f"\n📋 Final Transaction Summary:")
            print(f"ETF: {buy_rec['etf_name']}")
            print(f"Target Investment: ₹{investment_amount:,.2f}")
            print(f"Suggested Quantity: {suggested_qty}")
            print(f"Actual Quantity: {quantity}")
            print(f"Price per Unit: ₹{actual_price:.2f}")
            print(f"Total Amount: ₹{total_amount:,.2f}")
            print(f"Amount Difference: ₹{total_amount - investment_amount:,.2f}")
            
            if abs(total_amount - investment_amount) > investment_amount * 0.1:  # >10% difference
                print(f"⚠️ Warning: Actual amount differs significantly from target investment")
            
            confirm = input("\nConfirm transaction? (y/n): ").lower()
            if confirm != 'y':
                print("Transaction cancelled.")
                return
            
            # Execute transaction
            result = self.strategy.execute_buy_recommendation(buy_rec, quantity, actual_price)
            
            if result['success']:
                print(f"\n✅ {result['message']}")
                print(f"Total Amount: ₹{result['total_amount']:,.2f}")
                print(f"Transaction ID: {result['transaction_id']}")
                
                # Show investment efficiency
                utilization = (result['total_amount'] / investment_amount) * 100
                print(f"Investment Utilization: {utilization:.1f}%")
            else:
                print(f"\n❌ {result['message']}")
                
        except ValueError:
            print("❌ Invalid input. Please enter valid numbers.")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def execute_sell_transaction(self):
        """Execute a sell transaction"""
        print("\n💵 Execute Sell Transaction")
        print("-" * 35)
        
        # Get current recommendation
        recommendations = self.strategy.get_daily_recommendations()
        sell_rec = recommendations['sell_recommendation']
        
        if sell_rec['action'] == 'no_action':
            print("❌ No sell recommendation available today.")
            print(f"Reason: {sell_rec['reason']}")
            return
        
        print(f"Recommended ETF: {sell_rec['etf_name']}")
        print(f"Current Price: ₹{sell_rec['current_price']:.2f}")
        print(f"Expected Profit: {sell_rec['profit_percent']:.2f}%")
        print(f"Reason: {sell_rec['reason']}")
        
        try:
            quantity = int(input("\nEnter quantity to sell: "))
            actual_price = float(input(f"Enter actual price (current: ₹{sell_rec['current_price']:.2f}): "))
            
            # Validate inputs
            is_valid, validation_msg = self.strategy.validate_transaction_inputs(quantity, actual_price)
            if not is_valid:
                print(f"❌ {validation_msg}")
                return
            
            # Confirm transaction
            total_amount = quantity * actual_price
            print(f"\n📋 Transaction Summary:")
            print(f"ETF: {sell_rec['etf_name']}")
            print(f"Quantity: {quantity}")
            print(f"Price: ₹{actual_price:.2f}")
            print(f"Total Amount: ₹{total_amount:,.2f}")
            
            confirm = input("\nConfirm transaction? (y/n): ").lower()
            if confirm != 'y':
                print("Transaction cancelled.")
                return
            
            # Execute transaction
            result = self.strategy.execute_sell_recommendation(sell_rec, quantity, actual_price)
            
            if result['success']:
                print(f"\n✅ {result['message']}")
                print(f"Profit: ₹{result['profit']:,.2f} ({result['profit_percent']:.2f}%)")
            else:
                print(f"\n❌ {result['message']}")
                
        except ValueError:
            print("❌ Invalid input. Please enter valid numbers.")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def view_statistics(self):
        """Display trading statistics"""
        print("\n📋 Trading Statistics")
        print("-" * 30)
        
        stats = self.strategy.get_strategy_statistics()
        
        print(f"Total Buy Transactions: {stats['total_buy_transactions']}")
        print(f"Total Sell Transactions: {stats['total_sell_transactions']}")
        print(f"Profitable Sells: {stats['profitable_sells']}")
        print(f"Loss Sells: {stats['loss_sells']}")
        print(f"Win Rate: {stats['win_rate_percent']:.2f}%")
        print(f"Total Realized Profit: ₹{stats['total_realized_profit']:,.2f}")
        print(f"Average Profit per Sell: ₹{stats['average_profit_per_sell']:,.2f}")
    
    def load_sample_data(self):
        """Load sample data for testing"""
        print("\n🔄 Loading Sample Data")
        print("-" * 25)
        
        # Sample ETF price data
        sample_data = [
            ("GOLDBEES", 45.50, 44.20),
            ("KOTAKGOLD", 12.30, 12.10),
            ("SETFGOLD", 50.75, 49.80),
            ("HNGSNGBEES", 35.20, 36.10),
            ("MAHKTECH", 28.90, 29.50),
            ("ITBEES", 42.15, 41.80),
            ("BANKBEES", 38.60, 39.20),
            ("NIFTYBEES", 155.30, 154.50)
        ]
        
        try:
            for etf_name, cmp, dma_20 in sample_data:
                self.data_manager.update_etf_price(etf_name, cmp, dma_20)
            
            print(f"✅ Loaded {len(sample_data)} sample ETF prices successfully!")
            print("You can now test the strategy recommendations.")
            
        except Exception as e:
            print(f"❌ Error loading sample data: {e}")
    
    def update_etf_volume_status(self):
        """Update volume status for all ETFs"""
        print("\n📊 Update ETF Volume Status")
        print("-" * 30)
        
        print("This will fetch volume data for all ETFs and determine qualification based on")
        print(f"minimum volume threshold: {self.volume_filter.config['minimum_volume_threshold']:,}")
        print("\n⚠️ This process may take several minutes due to rate limiting")
        
        confirm = input("Continue with volume status update? (y/n): ").lower()
        if confirm != 'y':
            print("Update cancelled")
            return
        
        try:
            qualified_count, total_processed = self.volume_filter.update_all_etf_volume_status()
            
            print(f"\n✅ Volume status update completed!")
            print(f"   Processed: {total_processed} ETFs")
            print(f"   Qualified: {qualified_count} ETFs")
            print(f"   Disqualified: {total_processed - qualified_count} ETFs")
            
        except Exception as e:
            print(f"❌ Error updating volume status: {e}")
    
    def view_volume_report(self):
        """Display volume qualification report"""
        print("\n📊 ETF Volume Report")
        print("-" * 25)
        
        try:
            self.volume_filter.display_volume_report()
        except Exception as e:
            print(f"❌ Error displaying volume report: {e}")
    
    def set_volume_threshold(self):
        """Set minimum volume threshold"""
        print("\n📊 Set Volume Threshold")
        print("-" * 25)
        
        current_threshold = self.volume_filter.config['minimum_volume_threshold']
        print(f"Current threshold: {current_threshold:,}")
        
        try:
            new_threshold = int(input("Enter new minimum volume threshold: "))
            
            if new_threshold < 1000:
                print("⚠️ Very low threshold may include illiquid ETFs")
            elif new_threshold > 1000000:
                print("⚠️ Very high threshold may exclude many ETFs")
            
            confirm = input(f"Set threshold to {new_threshold:,}? (y/n): ").lower()
            if confirm == 'y':
                self.volume_filter.set_volume_threshold(new_threshold)
                print(f"✅ Volume threshold updated to {new_threshold:,}")
            else:
                print("Threshold change cancelled")
                
        except ValueError:
            print("❌ Invalid number entered")
        except Exception as e:
            print(f"❌ Error setting threshold: {e}")
    
    def toggle_volume_filtering(self):
        """Toggle volume filtering on/off"""
        print("\n📊 Toggle Volume Filtering")
        print("-" * 30)
        
        current_status = self.volume_filter.config['volume_check_enabled']
        strategy_status = self.strategy.volume_filtering_enabled
        
        print(f"Volume Filter Status: {'✅ Enabled' if current_status else '❌ Disabled'}")
        print(f"Strategy Integration: {'✅ Enabled' if strategy_status else '❌ Disabled'}")
        
        print("\nOptions:")
        print("1. Enable volume filtering")
        print("2. Disable volume filtering")
        print("3. Cancel")
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == '1':
            self.volume_filter.enable_volume_filter(True)
            self.strategy.volume_filtering_enabled = True
            print("✅ Volume filtering enabled")
            print("   Only ETFs with volume > threshold will be eligible for trading")
            
        elif choice == '2':
            self.volume_filter.enable_volume_filter(False)
            self.strategy.volume_filtering_enabled = False
            print("❌ Volume filtering disabled")
            print("   All ETFs will be eligible for trading regardless of volume")
            
        elif choice == '3':
            print("No changes made")
            
        else:
            print("❌ Invalid choice")


if __name__ == "__main__":
    cli = EnhancedETFCLI()
    cli.run()