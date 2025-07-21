#!/usr/bin/env python3
"""
Demo script for ETF Trading Strategy System
Shows how to use the system programmatically
"""

from etf_data_manager import ETFDataManager
from trading_strategy import ETFTradingStrategy
import json

def main():
    print("🤖 ETF Trading Strategy System Demo")
    print("=" * 45)
    
    # Initialize system
    data_manager = ETFDataManager()
    strategy = ETFTradingStrategy(data_manager)
    
    # Load ETF list
    print("\n1️⃣ Loading ETF list...")
    etf_names = data_manager.load_etf_list_from_excel("etf-list.xlsx")
    print(f"✅ Loaded {len(etf_names)} ETFs from Excel file")
    
    # Add sample price data
    print("\n2️⃣ Adding sample price data...")
    sample_data = [
        ("GOLDBEES", 45.50, 44.20),    # +2.94% deviation (rank 5)
        ("KOTAKGOLD", 12.30, 12.10),   # +1.65% deviation (rank 4) 
        ("SETFGOLD", 50.75, 49.80),    # +1.91% deviation (rank 3)
        ("HNGSNGBEES", 35.20, 36.10),  # -2.49% deviation (rank 1) - most fallen
        ("MAHKTECH", 28.90, 29.50),    # -2.03% deviation (rank 2)
        ("ITBEES", 42.15, 41.80),      # +0.84% deviation
        ("BANKBEES", 38.60, 39.20),    # -1.53% deviation
        ("NIFTYBEES", 155.30, 154.50)  # +0.52% deviation
    ]
    
    for etf_name, cmp, dma_20 in sample_data:
        data_manager.update_etf_price(etf_name, cmp, dma_20)
        deviation = ((cmp - dma_20) / dma_20) * 100
        print(f"   {etf_name}: CMP=₹{cmp:.2f}, 20DMA=₹{dma_20:.2f}, Deviation={deviation:.2f}%")
    
    # Show ETF rankings
    print("\n3️⃣ ETF Rankings (by deviation from 20-day moving average):")
    rankings = data_manager.get_etf_rankings()
    print(f"{'Rank':<6}{'ETF':<12}{'CMP':<10}{'20DMA':<10}{'Deviation'}")
    print("-" * 50)
    for i, (etf_name, cmp, dma_20, deviation) in enumerate(rankings[:8], 1):
        print(f"{i:<6}{etf_name:<12}₹{cmp:<9.2f}₹{dma_20:<9.2f}{deviation:>8.2f}%")
    
    # Get daily strategy recommendations
    print("\n4️⃣ Daily Strategy Recommendations:")
    recommendations = strategy.get_daily_recommendations()
    
    buy_rec = recommendations['buy_recommendation']
    print(f"\n🟢 BUY RECOMMENDATION:")
    print(f"   Action: {buy_rec['action']}")
    if buy_rec['action'] != 'no_action':
        print(f"   ETF: {buy_rec['etf_name']}")
        print(f"   Rank: {buy_rec.get('rank', 'N/A')}")
        print(f"   Current Price: ₹{buy_rec.get('cmp', buy_rec.get('current_price', 'N/A'))}")
        print(f"   Deviation: {buy_rec.get('deviation_percent', 'N/A'):.2f}%")
        print(f"   Reason: {buy_rec['reason']}")
    
    # Simulate a buy transaction
    print("\n5️⃣ Simulating Buy Transaction:")
    if buy_rec['action'] in ['buy_new', 'average_down']:
        etf_name = buy_rec['etf_name']
        quantity = 10
        actual_price = buy_rec.get('cmp', buy_rec.get('current_price', 0))
        
        result = strategy.execute_buy_recommendation(buy_rec, quantity, actual_price)
        if result['success']:
            print(f"✅ {result['message']}")
            print(f"   Total Amount: ₹{result['total_amount']:,.2f}")
        else:
            print(f"❌ {result['message']}")
    
    # Show portfolio after purchase
    print("\n6️⃣ Portfolio After Purchase:")
    portfolio = data_manager.get_portfolio_summary()
    print(f"   Total ETFs: {portfolio['total_etfs']}")
    print(f"   Total Investment: ₹{portfolio['total_investments']:,.2f}")
    print(f"   Current Value: ₹{portfolio['current_value']:,.2f}")
    print(f"   P&L: ₹{portfolio['total_profit_loss']:,.2f}")
    
    # Simulate price change to trigger profit
    print("\n7️⃣ Simulating Price Increase (to trigger sell signal):")
    if buy_rec['action'] != 'no_action':
        etf_name = buy_rec['etf_name']
        original_price = buy_rec.get('cmp', buy_rec.get('current_price', 0))
        new_price = original_price * 1.08  # 8% increase to trigger 6% profit threshold
        
        data_manager.update_etf_price(etf_name, new_price, original_price)
        print(f"   Updated {etf_name} price from ₹{original_price:.2f} to ₹{new_price:.2f} (+8%)")
    
    # Check for sell recommendation
    print("\n8️⃣ Checking for Sell Opportunities:")
    new_recommendations = strategy.get_daily_recommendations()
    sell_rec = new_recommendations['sell_recommendation']
    
    print(f"\n🔴 SELL RECOMMENDATION:")
    print(f"   Action: {sell_rec['action']}")
    if sell_rec['action'] != 'no_action':
        print(f"   ETF: {sell_rec['etf_name']}")
        print(f"   Current Price: ₹{sell_rec['current_price']:.2f}")
        print(f"   Profit: {sell_rec['profit_percent']:.2f}%")
        print(f"   Reason: {sell_rec['reason']}")
        
        # Simulate sell transaction
        print("\n9️⃣ Simulating Sell Transaction:")
        quantity = 5  # Sell partial position
        actual_price = sell_rec['current_price']
        
        result = strategy.execute_sell_recommendation(sell_rec, quantity, actual_price)
        if result['success']:
            print(f"✅ {result['message']}")
            print(f"   Profit: ₹{result['profit']:,.2f} ({result['profit_percent']:.2f}%)")
    
    # Final portfolio and statistics
    print("\n🔟 Final Portfolio and Statistics:")
    final_portfolio = data_manager.get_portfolio_summary()
    stats = strategy.get_strategy_statistics()
    
    print(f"\n📊 Portfolio Summary:")
    print(f"   Total ETFs: {final_portfolio['total_etfs']}")
    print(f"   Total Investment: ₹{final_portfolio['total_investments']:,.2f}")
    print(f"   Current Value: ₹{final_portfolio['current_value']:,.2f}")
    print(f"   P&L: ₹{final_portfolio['total_profit_loss']:,.2f}")
    
    print(f"\n📈 Trading Statistics:")
    print(f"   Buy Transactions: {stats['total_buy_transactions']}")
    print(f"   Sell Transactions: {stats['total_sell_transactions']}")
    print(f"   Win Rate: {stats['win_rate_percent']:.2f}%")
    print(f"   Total Realized Profit: ₹{stats['total_realized_profit']:,.2f}")
    
    print(f"\n✅ Demo completed successfully!")
    print(f"📄 Data saved to: etf_data.json")
    print(f"🚀 Start the CLI: python3 etf_cli.py")
    print(f"🤖 Start the Telegram bot: python3 telegram_bot.py")

if __name__ == "__main__":
    main()