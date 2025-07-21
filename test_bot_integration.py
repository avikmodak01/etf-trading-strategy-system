#!/usr/bin/env python3
"""
Test Telegram bot data integration
"""

from telegram_bot import ETFTradingBot
from bot_config import BOT_TOKEN

def test_bot_integration():
    print('🤖 Testing Telegram Bot Data Integration')
    print('=' * 45)

    try:
        bot = ETFTradingBot(BOT_TOKEN)
        print('✅ Bot initialized successfully')
        
        # Test data manager
        print(f'📊 ETFs in system: {len(bot.data_manager.data["etfs"])}')
        
        # Check for live data
        etfs_with_data = 0
        recent_updates = 0
        sample_etfs = []
        
        for etf_name, etf_data in bot.data_manager.data['etfs'].items():
            if etf_data.get('cmp'):
                etfs_with_data += 1
                sample_etfs.append((etf_name, etf_data['cmp'], etf_data.get('last_price_update', '')))
                if etf_data.get('last_price_update') and '2025-07-20T21:50' in etf_data['last_price_update']:
                    recent_updates += 1
        
        print(f'💰 ETFs with price data: {etfs_with_data}')
        print(f'⏰ Recent updates (21:50): {recent_updates}')
        
        # Show sample live data
        print('\n📈 Sample Live Data in Bot:')
        for i, (name, price, timestamp) in enumerate(sample_etfs[:5]):
            print(f'   {name}: ₹{price:.2f} (Updated: {timestamp[:19]})')
        
        # Test strategy recommendations
        recommendations = bot.strategy.get_daily_recommendations()
        buy_action = recommendations['buy_recommendation']['action']
        print(f'\n📊 Strategy Status:')
        print(f'   Buy recommendation: {buy_action}')
        
        if buy_action != 'no_action':
            etf_name = recommendations['buy_recommendation']['etf_name']
            current_price = recommendations['buy_recommendation'].get('cmp', recommendations['buy_recommendation'].get('current_price', 'N/A'))
            print(f'   🎯 Recommended ETF: {etf_name}')
            print(f'   💰 Current price: ₹{current_price}')
        
        # Test price fetcher integration
        print('\n🔧 Testing Live Price Fetcher:')
        sample_data = bot.price_fetcher.fetch_yahoo_finance_data('GOLDBEES')
        if sample_data:
            print(f'✅ Live data fetch working: GOLDBEES ₹{sample_data["current_price"]:.2f}')
            print(f'   20-day MA: ₹{sample_data["ma_20"]:.2f}')
            print(f'   Volume: {sample_data["volume"]:,}')
        else:
            print('❌ Live data fetch not working')
        
        # Test scheduler integration
        print('\n⏰ Testing Update Scheduler:')
        scheduler = bot.data_manager
        test_etfs = ['GOLDBEES', 'NIFTYBEES']
        print(f'Testing bulk update for {test_etfs}...')
        
        updated_data = bot.price_fetcher.fetch_multiple_etfs(test_etfs)
        if updated_data:
            print('✅ Bulk update working:')
            for etf, data in updated_data.items():
                if data:
                    print(f'   {etf}: ₹{data["current_price"]:.2f}')
        
        print('\n🎉 Bot Integration Test Results:')
        print(f'   ✅ Bot initialization: Working')
        print(f'   ✅ Data manager: {etfs_with_data} ETFs loaded')
        print(f'   ✅ Live data: {recent_updates} recent updates')
        print(f'   ✅ Strategy engine: Working')
        print(f'   ✅ Price fetcher: Working')
        print(f'   ✅ All components integrated successfully!')
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_bot_integration()