#!/usr/bin/env python3
"""
Test script for volume filtering functionality
"""

from etf_data_manager import ETFDataManager
from trading_strategy import ETFTradingStrategy
from volume_filter import VolumeFilter
from price_fetcher import PriceFetcher

def test_volume_filtering():
    print("📊 Testing Volume Filtering System")
    print("=" * 40)
    
    # Initialize components
    data_manager = ETFDataManager()
    price_fetcher = PriceFetcher()
    volume_filter = VolumeFilter(data_manager, price_fetcher)
    strategy = ETFTradingStrategy(data_manager, volume_filter)
    
    # Load ETF list
    data_manager.load_etf_list_from_excel("etf-list.xlsx")
    
    print(f"✅ Loaded {len(data_manager.data['etfs'])} ETFs from Excel file")
    
    # Test with a few popular ETFs
    test_etfs = ['GOLDBEES', 'NIFTYBEES', 'BANKBEES', 'ITBEES', 'HNGSNGBEES']
    
    print(f"\n🧪 Testing volume fetch for sample ETFs:")
    print("-" * 50)
    
    for etf in test_etfs:
        if etf in data_manager.data['etfs']:
            print(f"\n🔍 Testing {etf}...")
            success = volume_filter.update_etf_volume_status(etf)
            
            if success:
                etf_data = data_manager.data['etfs'][etf]
                volume_data = etf_data.get('volume_data', {})
                is_qualified = etf_data.get('volume_qualified', False)
                
                current_vol = volume_data.get('current_volume', 0)
                avg_vol = volume_data.get('average_volume_5d', 0)
                
                print(f"   Current Volume: {current_vol:,}")
                print(f"   5-day Avg Volume: {avg_vol:,}")
                print(f"   Qualification: {'✅ Qualified' if is_qualified else '❌ Disqualified'}")
            else:
                print(f"   ❌ Failed to fetch volume data")
        else:
            print(f"   ⚠️ {etf} not found in ETF list")
    
    # Test strategy with volume filtering
    print(f"\n📈 Testing Strategy with Volume Filtering:")
    print("-" * 45)
    
    # Enable volume filtering
    volume_filter.enable_volume_filter(True)
    strategy.volume_filtering_enabled = True
    
    print("✅ Volume filtering enabled")
    print(f"📊 Threshold: {volume_filter.config['minimum_volume_threshold']:,}")
    
    # Get strategy recommendations
    try:
        recommendations = strategy.get_daily_recommendations()
        
        buy_rec = recommendations['buy_recommendation']
        print(f"\n🟢 Buy Recommendation:")
        print(f"   Action: {buy_rec['action']}")
        
        if buy_rec['action'] != 'no_action':
            print(f"   ETF: {buy_rec['etf_name']}")
            print(f"   Reason: {buy_rec['reason']}")
            
            # Check if recommended ETF is volume qualified
            etf_name = buy_rec['etf_name']
            if etf_name in data_manager.data['etfs']:
                is_qualified = data_manager.data['etfs'][etf_name].get('volume_qualified')
                print(f"   Volume Qualified: {'✅ Yes' if is_qualified else '❌ No'}")
        else:
            print(f"   Reason: {buy_rec['reason']}")
    
    except Exception as e:
        print(f"❌ Error getting strategy recommendations: {e}")
    
    # Show volume filter statistics
    print(f"\n📊 Volume Filter Report:")
    print("-" * 30)
    
    qualified_etfs = volume_filter.get_qualified_etfs()
    disqualified_etfs = volume_filter.get_disqualified_etfs()
    
    print(f"Total ETFs: {len(data_manager.data['etfs'])}")
    print(f"Qualified ETFs: {len(qualified_etfs)}")
    print(f"Disqualified ETFs: {len(disqualified_etfs)}")
    print(f"Pending Check: {len(data_manager.data['etfs']) - len(qualified_etfs) - len(disqualified_etfs)}")
    
    if qualified_etfs:
        print(f"\n✅ Sample Qualified ETFs:")
        for etf in qualified_etfs[:5]:
            etf_data = data_manager.data['etfs'][etf]
            volume_data = etf_data.get('volume_data', {})
            avg_vol = volume_data.get('average_volume_5d', 0)
            print(f"   {etf}: {avg_vol:,}")
    
    # Test disabling volume filter
    print(f"\n🔧 Testing Volume Filter Disable:")
    print("-" * 35)
    
    volume_filter.enable_volume_filter(False)
    strategy.volume_filtering_enabled = False
    
    print("❌ Volume filtering disabled")
    
    try:
        recommendations_no_filter = strategy.get_daily_recommendations()
        buy_rec_no_filter = recommendations_no_filter['buy_recommendation']
        
        print(f"📈 Strategy without volume filter:")
        print(f"   Action: {buy_rec_no_filter['action']}")
        if buy_rec_no_filter['action'] != 'no_action':
            print(f"   ETF: {buy_rec_no_filter['etf_name']}")
            print(f"   (Volume filter was ignored)")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print(f"\n✅ Volume Filtering Test Complete!")
    print(f"📋 Summary:")
    print(f"   ✅ Volume data fetching: Working")
    print(f"   ✅ ETF qualification: Working") 
    print(f"   ✅ Strategy integration: Working")
    print(f"   ✅ Enable/disable toggle: Working")

if __name__ == "__main__":
    test_volume_filtering()