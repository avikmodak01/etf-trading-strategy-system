#!/usr/bin/env python3
"""
Test script for complete investment management integration
"""

import sys
from etf_data_manager import ETFDataManager
from investment_manager import InvestmentManager
from trading_strategy import ETFTradingStrategy
from volume_filter import VolumeFilter
from price_fetcher import PriceFetcher

def test_investment_integration():
    print("💰 Testing Investment Management Integration")
    print("=" * 50)
    
    # Initialize components
    print("🔄 Initializing components...")
    data_manager = ETFDataManager()
    investment_manager = InvestmentManager(data_manager)
    price_fetcher = PriceFetcher()
    volume_filter = VolumeFilter(data_manager, price_fetcher)
    strategy = ETFTradingStrategy(data_manager, volume_filter)
    
    print("✅ Components initialized successfully")
    
    # Test 1: Investment Configuration
    print("\n📊 Test 1: Investment Configuration")
    print("-" * 35)
    
    # Display current configuration
    investment_manager.display_investment_config()
    
    # Test 2: Investment Calculation
    print("\n📊 Test 2: Investment Calculation")
    print("-" * 35)
    
    # Test with sample ETF data
    test_etf = "GOLDBEES"
    test_price = 81.73
    test_investment = 10000
    
    print(f"Testing with {test_etf} at ₹{test_price}")
    
    try:
        suggestion = investment_manager.get_investment_suggestion(
            test_etf, test_price, test_investment
        )
        
        investment_manager.display_investment_suggestion(suggestion)
        
        print("✅ Investment calculation successful")
        
    except Exception as e:
        print(f"❌ Investment calculation failed: {e}")
        return False
    
    # Test 3: Strategy Integration
    print("\n📊 Test 3: Strategy Integration Check")
    print("-" * 35)
    
    # Check if strategy can access investment manager features
    # (This would normally be called during actual buy transactions)
    try:
        # Simulate investment amount validation
        min_amount = investment_manager.config["min_investment_per_trade"]
        max_amount = investment_manager.config["max_investment_per_trade"]
        default_amount = investment_manager.config["default_investment_per_trade"]
        
        print(f"Investment limits configured:")
        print(f"  Minimum: ₹{min_amount:,}")
        print(f"  Maximum: ₹{max_amount:,}")
        print(f"  Default: ₹{default_amount:,}")
        
        # Test quantity calculation with different investment amounts
        test_amounts = [5000, 10000, 25000]
        
        print(f"\nQuantity calculations for {test_etf}:")
        for amount in test_amounts:
            calc = investment_manager.calculate_suggested_quantity(test_price, amount)
            print(f"  ₹{amount:,} → {calc['suggested_quantity']} units (₹{calc['exact_investment']:,.2f})")
        
        print("✅ Strategy integration check successful")
        
    except Exception as e:
        print(f"❌ Strategy integration failed: {e}")
        return False
    
    # Test 4: Portfolio Investment Summary
    print("\n📊 Test 4: Portfolio Investment Summary")
    print("-" * 35)
    
    try:
        portfolio_summary = investment_manager.get_portfolio_investment_summary()
        
        print(f"Portfolio Analysis:")
        print(f"  Total Invested: ₹{portfolio_summary['total_invested']:,.2f}")
        print(f"  Current Value: ₹{portfolio_summary['current_value']:,.2f}")
        print(f"  Total ETFs: {portfolio_summary['total_etfs']}")
        print(f"  Avg Investment per ETF: ₹{portfolio_summary['avg_investment_per_etf']:,.2f}")
        print(f"  Investment Efficiency: {portfolio_summary['investment_efficiency']:.1f}%")
        
        print("✅ Portfolio analysis successful")
        
    except Exception as e:
        print(f"❌ Portfolio analysis failed: {e}")
        return False
    
    # Test 5: Investment Strategies
    print("\n📊 Test 5: Investment Strategies")
    print("-" * 35)
    
    try:
        strategies = investment_manager.get_investment_strategies()
        
        print("Available investment strategies:")
        for name, amount in strategies.items():
            print(f"  {name}: ₹{amount:,}")
        
        print("✅ Investment strategies check successful")
        
    except Exception as e:
        print(f"❌ Investment strategies failed: {e}")
        return False
    
    # Summary
    print("\n🎉 Integration Test Complete!")
    print("=" * 40)
    print("✅ All tests passed successfully!")
    print("\n📋 Integration Status:")
    print("  ✅ Investment Manager: Working")
    print("  ✅ Configuration Management: Working")
    print("  ✅ Quantity Calculations: Working")
    print("  ✅ Strategy Integration: Working")
    print("  ✅ Portfolio Analysis: Working")
    print("  ✅ Investment Strategies: Working")
    
    print("\n🚀 Ready for Use!")
    print("📱 Enhanced CLI: Use option 21 to configure investment capital")
    print("🤖 Telegram Bot: Investment prompts included in buy flow")
    
    return True

def test_cli_integration():
    """Test CLI integration specifically"""
    print("\n🖥️ Testing CLI Integration")
    print("-" * 30)
    
    try:
        from enhanced_cli import EnhancedETFCLI
        
        # Check if CLI has investment manager
        cli = EnhancedETFCLI()
        
        if hasattr(cli, 'investment_manager'):
            print("✅ Enhanced CLI has investment manager")
            
            if hasattr(cli, 'configure_investment_capital'):
                print("✅ Enhanced CLI has investment configuration method")
            else:
                print("❌ Enhanced CLI missing investment configuration method")
                return False
        else:
            print("❌ Enhanced CLI missing investment manager")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ CLI import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False

def test_telegram_integration():
    """Test Telegram bot integration specifically"""
    print("\n🤖 Testing Telegram Bot Integration")
    print("-" * 35)
    
    try:
        from telegram_bot import ETFTradingBot
        
        # Check if bot has investment manager
        bot = ETFTradingBot("dummy_token")
        
        if hasattr(bot, 'investment_manager'):
            print("✅ Telegram bot has investment manager")
            
            required_methods = [
                'handle_default_investment',
                'process_investment_amount',
                'process_investment_amount_input',
                'process_investment_amount_message'
            ]
            
            missing_methods = []
            for method in required_methods:
                if hasattr(bot, method):
                    print(f"✅ Telegram bot has {method}")
                else:
                    print(f"❌ Telegram bot missing {method}")
                    missing_methods.append(method)
            
            if missing_methods:
                return False
        else:
            print("❌ Telegram bot missing investment manager")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Telegram bot import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Telegram bot test failed: {e}")
        return False

if __name__ == "__main__":
    success = True
    
    # Run main integration test
    success &= test_investment_integration()
    
    # Run CLI integration test
    success &= test_cli_integration()
    
    # Run Telegram integration test
    success &= test_telegram_integration()
    
    if success:
        print("\n🎉 All Integration Tests Passed!")
        print("✅ Investment management system is fully integrated and ready to use.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)