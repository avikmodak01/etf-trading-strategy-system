#!/usr/bin/env python3
"""
Command Line Interface for ETF Trading Strategy
"""

import sys
from etf_data_manager import ETFDataManager
from trading_strategy import ETFTradingStrategy
import json

class ETFCommandLineInterface:
    def __init__(self):
        self.data_manager = ETFDataManager()
        self.strategy = ETFTradingStrategy(self.data_manager)
        
        # Load ETF list on startup
        try:
            self.data_manager.load_etf_list_from_excel("etf-list.xlsx")
            print("✅ ETF list loaded successfully")
        except Exception as e:
            print(f"❌ Error loading ETF list: {e}")
    
    def display_menu(self):
        """Display main menu"""
        print("\n" + "="*50)
        print("🤖 ETF Trading Strategy System")
        print("="*50)
        print("1. 📊 Get Daily Strategy Recommendations")
        print("2. 💰 Update ETF Prices")
        print("3. 📈 View Portfolio")
        print("4. 🏆 View ETF Rankings")
        print("5. 💸 Execute Buy Transaction")
        print("6. 💵 Execute Sell Transaction")
        print("7. 📋 View Statistics")
        print("8. 🔄 Load Sample Data")
        print("9. ❌ Exit")
        print("="*50)
    
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
    
    def update_etf_prices(self):
        """Update ETF prices"""
        print("\n💰 Update ETF Prices")
        print("-" * 30)
        print("Enter ETF price data in format: ETF_NAME,CMP,20DMA")
        print("Example: GOLDBEES,45.50,44.20")
        print("Type 'done' when finished, 'cancel' to abort")
        
        updated_count = 0
        while True:
            data = input("\nEnter price data: ").strip()
            
            if data.lower() == 'done':
                break
            elif data.lower() == 'cancel':
                print("Update cancelled.")
                return
            
            try:
                parts = data.split(',')
                if len(parts) != 3:
                    print("❌ Invalid format. Use: ETF_NAME,CMP,20DMA")
                    continue
                
                etf_name, cmp_str, dma_str = [p.strip() for p in parts]
                cmp = float(cmp_str)
                dma_20 = float(dma_str)
                
                self.data_manager.update_etf_price(etf_name, cmp, dma_20)
                print(f"✅ Updated {etf_name}: CMP=₹{cmp:.2f}, 20DMA=₹{dma_20:.2f}")
                updated_count += 1
                
            except ValueError:
                print("❌ Invalid numbers. Please check your input.")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print(f"\n✅ Updated {updated_count} ETF(s) successfully!")
    
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
        """Execute a buy transaction"""
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
        print(f"Suggested Price: ₹{current_price:.2f}")
        print(f"Reason: {buy_rec['reason']}")
        
        try:
            quantity = int(input("\nEnter quantity to buy: "))
            actual_price = float(input(f"Enter actual price (suggested: ₹{current_price:.2f}): "))
            
            # Validate inputs
            is_valid, validation_msg = self.strategy.validate_transaction_inputs(quantity, actual_price)
            if not is_valid:
                print(f"❌ {validation_msg}")
                return
            
            # Confirm transaction
            total_amount = quantity * actual_price
            print(f"\n📋 Transaction Summary:")
            print(f"ETF: {buy_rec['etf_name']}")
            print(f"Quantity: {quantity}")
            print(f"Price: ₹{actual_price:.2f}")
            print(f"Total Amount: ₹{total_amount:,.2f}")
            
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
    
    def run(self):
        """Run the command line interface"""
        print("🤖 ETF Trading Strategy System")
        print("Welcome! This system implements a systematic ETF trading strategy.")
        
        while True:
            try:
                self.display_menu()
                choice = input("\nEnter your choice (1-9): ").strip()
                
                if choice == '1':
                    self.get_daily_strategy()
                elif choice == '2':
                    self.update_etf_prices()
                elif choice == '3':
                    self.view_portfolio()
                elif choice == '4':
                    self.view_rankings()
                elif choice == '5':
                    self.execute_buy_transaction()
                elif choice == '6':
                    self.execute_sell_transaction()
                elif choice == '7':
                    self.view_statistics()
                elif choice == '8':
                    self.load_sample_data()
                elif choice == '9':
                    print("\n👋 Thank you for using ETF Trading Strategy System!")
                    break
                else:
                    print("❌ Invalid choice. Please enter a number between 1-9.")
                
                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {e}")
                input("Press Enter to continue...")

if __name__ == "__main__":
    cli = ETFCommandLineInterface()
    cli.run()