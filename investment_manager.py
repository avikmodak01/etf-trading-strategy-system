#!/usr/bin/env python3
"""
Investment Manager - Handles investment capital and quantity calculations
"""

import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from etf_data_manager import ETFDataManager

class InvestmentManager:
    """Manages investment capital per trade and quantity calculations"""
    
    def __init__(self, data_manager: ETFDataManager):
        self.data_manager = data_manager
        self.config_file = "investment_config.json"
        self.load_investment_config()
    
    def load_investment_config(self):
        """Load investment configuration"""
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            # Create default configuration
            self.config = {
                "default_investment_per_trade": 10000,  # ₹10,000 per trade
                "min_investment_per_trade": 1000,       # Minimum ₹1,000
                "max_investment_per_trade": 100000,     # Maximum ₹1,00,000
                "investment_strategies": {
                    "conservative": 5000,   # ₹5,000 per trade
                    "balanced": 10000,      # ₹10,000 per trade
                    "aggressive": 25000     # ₹25,000 per trade
                },
                "settings": {
                    "round_down_quantities": True,      # Round down to avoid over-investment
                    "min_quantity": 1,                  # Minimum 1 unit
                    "max_quantity": 1000,              # Maximum 1000 units per trade
                    "allow_fractional": False,          # No fractional shares
                    "buffer_percentage": 2.0            # 2% buffer for price fluctuations
                },
                "last_updated": datetime.now().isoformat(),
                "version": "1.0"
            }
            self.save_investment_config()
    
    def save_investment_config(self):
        """Save investment configuration"""
        self.config["last_updated"] = datetime.now().isoformat()
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2, default=str)
    
    def set_default_investment_amount(self, amount: float):
        """Set default investment amount per trade"""
        if amount < self.config["min_investment_per_trade"]:
            raise ValueError(f"Investment amount must be at least ₹{self.config['min_investment_per_trade']:,}")
        
        if amount > self.config["max_investment_per_trade"]:
            raise ValueError(f"Investment amount cannot exceed ₹{self.config['max_investment_per_trade']:,}")
        
        self.config["default_investment_per_trade"] = amount
        self.save_investment_config()
        
        print(f"✅ Default investment per trade set to ₹{amount:,.2f}")
    
    def calculate_suggested_quantity(self, etf_price: float, investment_amount: float = None) -> Dict:
        """Calculate suggested quantity based on investment amount and ETF price"""
        if investment_amount is None:
            investment_amount = self.config["default_investment_per_trade"]
        
        # Validate investment amount
        if investment_amount < self.config["min_investment_per_trade"]:
            raise ValueError(f"Investment amount must be at least ₹{self.config['min_investment_per_trade']:,}")
        
        if investment_amount > self.config["max_investment_per_trade"]:
            raise ValueError(f"Investment amount cannot exceed ₹{self.config['max_investment_per_trade']:,}")
        
        # Apply buffer for price fluctuations
        buffer_percentage = self.config["settings"]["buffer_percentage"]
        effective_price = etf_price * (1 + buffer_percentage / 100)
        
        # Calculate raw quantity
        raw_quantity = investment_amount / effective_price
        
        # Round based on settings
        if self.config["settings"]["round_down_quantities"]:
            suggested_quantity = int(raw_quantity)  # Round down
        else:
            suggested_quantity = round(raw_quantity)  # Round to nearest
        
        # Apply min/max constraints
        min_qty = self.config["settings"]["min_quantity"]
        max_qty = self.config["settings"]["max_quantity"]
        
        suggested_quantity = max(min_qty, min(suggested_quantity, max_qty))
        
        # Calculate actual investment amounts
        exact_amount = suggested_quantity * etf_price
        max_possible_amount = suggested_quantity * effective_price
        
        return {
            "investment_amount": investment_amount,
            "etf_price": etf_price,
            "effective_price": effective_price,
            "raw_quantity": raw_quantity,
            "suggested_quantity": suggested_quantity,
            "exact_investment": exact_amount,
            "max_investment_with_buffer": max_possible_amount,
            "buffer_percentage": buffer_percentage,
            "utilization_percentage": (exact_amount / investment_amount) * 100
        }
    
    def get_investment_suggestion(self, etf_name: str, etf_price: float, investment_amount: float = None) -> Dict:
        """Get complete investment suggestion for an ETF"""
        calc = self.calculate_suggested_quantity(etf_price, investment_amount)
        
        # Add ETF-specific information
        suggestion = calc.copy()
        suggestion.update({
            "etf_name": etf_name,
            "recommendation_summary": {
                "invest": f"₹{calc['investment_amount']:,.2f}",
                "buy_quantity": calc['suggested_quantity'],
                "at_price": f"₹{etf_price:.2f}",
                "actual_cost": f"₹{calc['exact_investment']:,.2f}",
                "remaining_amount": f"₹{calc['investment_amount'] - calc['exact_investment']:,.2f}"
            }
        })
        
        return suggestion
    
    def display_investment_suggestion(self, suggestion: Dict):
        """Display formatted investment suggestion"""
        print(f"\n💰 Investment Suggestion for {suggestion['etf_name']}")
        print("=" * 45)
        
        print(f"📊 Investment Details:")
        print(f"   Target Investment: ₹{suggestion['investment_amount']:,.2f}")
        print(f"   ETF Price: ₹{suggestion['etf_price']:.2f}")
        print(f"   Buffer Price: ₹{suggestion['effective_price']:.2f} (+{suggestion['buffer_percentage']:.1f}%)")
        
        print(f"\n🎯 Recommended Purchase:")
        print(f"   Suggested Quantity: {suggestion['suggested_quantity']} units")
        print(f"   Exact Cost: ₹{suggestion['exact_investment']:,.2f}")
        print(f"   Utilization: {suggestion['utilization_percentage']:.1f}%")
        print(f"   Remaining: ₹{suggestion['investment_amount'] - suggestion['exact_investment']:,.2f}")
        
        if suggestion['utilization_percentage'] < 80:
            print(f"   ⚠️ Low utilization - consider increasing quantity or reducing investment amount")
        elif suggestion['utilization_percentage'] > 98:
            print(f"   ⚠️ High utilization - buffer may not be sufficient")
        else:
            print(f"   ✅ Good utilization - balanced investment")
    
    def get_investment_strategies(self) -> Dict:
        """Get predefined investment strategies"""
        return self.config["investment_strategies"]
    
    def set_investment_strategy(self, strategy_name: str):
        """Set investment amount based on predefined strategy"""
        strategies = self.config["investment_strategies"]
        
        if strategy_name not in strategies:
            available = ", ".join(strategies.keys())
            raise ValueError(f"Strategy '{strategy_name}' not found. Available: {available}")
        
        amount = strategies[strategy_name]
        self.set_default_investment_amount(amount)
        
        print(f"✅ Investment strategy set to '{strategy_name}' (₹{amount:,} per trade)")
    
    def create_custom_strategy(self, name: str, amount: float):
        """Create a custom investment strategy"""
        self.config["investment_strategies"][name] = amount
        self.save_investment_config()
        
        print(f"✅ Custom strategy '{name}' created with ₹{amount:,} per trade")
    
    def interactive_investment_setup(self):
        """Interactive setup for investment configuration"""
        print("\n💰 Investment Capital Configuration")
        print("=" * 40)
        
        current_amount = self.config["default_investment_per_trade"]
        print(f"Current default investment per trade: ₹{current_amount:,}")
        
        while True:
            print("\nOptions:")
            print("1. Set custom investment amount")
            print("2. Choose predefined strategy")
            print("3. Create custom strategy")
            print("4. View current configuration")
            print("5. Test quantity calculation")
            print("6. Exit")
            
            choice = input("\nEnter choice (1-6): ").strip()
            
            if choice == '1':
                try:
                    amount = float(input("Enter investment amount per trade: ₹"))
                    self.set_default_investment_amount(amount)
                except ValueError as e:
                    print(f"❌ Error: {e}")
                except Exception as e:
                    print(f"❌ Invalid amount: {e}")
            
            elif choice == '2':
                strategies = self.get_investment_strategies()
                print("\nAvailable strategies:")
                for name, amount in strategies.items():
                    print(f"   {name}: ₹{amount:,}")
                
                strategy = input("Enter strategy name: ").strip().lower()
                try:
                    self.set_investment_strategy(strategy)
                except ValueError as e:
                    print(f"❌ {e}")
            
            elif choice == '3':
                try:
                    name = input("Enter strategy name: ").strip()
                    amount = float(input("Enter investment amount: ₹"))
                    self.create_custom_strategy(name, amount)
                except ValueError:
                    print("❌ Invalid amount")
                except Exception as e:
                    print(f"❌ Error: {e}")
            
            elif choice == '4':
                self.display_investment_config()
            
            elif choice == '5':
                self.test_quantity_calculation()
            
            elif choice == '6':
                print("👋 Configuration complete!")
                break
            
            else:
                print("❌ Invalid choice")
    
    def display_investment_config(self):
        """Display current investment configuration"""
        print(f"\n💰 Current Investment Configuration")
        print("-" * 40)
        
        print(f"Default per trade: ₹{self.config['default_investment_per_trade']:,}")
        print(f"Min per trade: ₹{self.config['min_investment_per_trade']:,}")
        print(f"Max per trade: ₹{self.config['max_investment_per_trade']:,}")
        
        print(f"\n📊 Predefined Strategies:")
        for name, amount in self.config["investment_strategies"].items():
            current = " (current)" if amount == self.config["default_investment_per_trade"] else ""
            print(f"   {name}: ₹{amount:,}{current}")
        
        print(f"\n⚙️ Settings:")
        settings = self.config["settings"]
        print(f"   Round down quantities: {settings['round_down_quantities']}")
        print(f"   Min quantity: {settings['min_quantity']}")
        print(f"   Max quantity: {settings['max_quantity']}")
        print(f"   Price buffer: {settings['buffer_percentage']}%")
        
        print(f"\nLast updated: {self.config['last_updated'][:19]}")
    
    def test_quantity_calculation(self):
        """Test quantity calculation with sample data"""
        print(f"\n🧪 Test Quantity Calculation")
        print("-" * 30)
        
        try:
            etf_name = input("Enter ETF name (or press Enter for GOLDBEES): ").strip() or "GOLDBEES"
            price_input = input("Enter ETF price (or press Enter for ₹81.73): ").strip()
            etf_price = float(price_input) if price_input else 81.73
            
            amount_input = input(f"Enter investment amount (or press Enter for ₹{self.config['default_investment_per_trade']:,}): ").strip()
            investment_amount = float(amount_input) if amount_input else None
            
            suggestion = self.get_investment_suggestion(etf_name, etf_price, investment_amount)
            self.display_investment_suggestion(suggestion)
            
        except ValueError:
            print("❌ Invalid input")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def get_portfolio_investment_summary(self) -> Dict:
        """Get summary of total investments and capital allocation"""
        portfolio = self.data_manager.get_portfolio_summary()
        
        total_invested = portfolio["total_investments"]
        current_value = portfolio["current_value"]
        
        # Calculate average investment per holding
        if portfolio["total_etfs"] > 0:
            avg_investment_per_etf = total_invested / portfolio["total_etfs"]
        else:
            avg_investment_per_etf = 0
        
        # Get default per trade amount
        default_per_trade = self.config["default_investment_per_trade"]
        
        return {
            "total_invested": total_invested,
            "current_value": current_value,
            "total_etfs": portfolio["total_etfs"],
            "avg_investment_per_etf": avg_investment_per_etf,
            "default_per_trade": default_per_trade,
            "potential_new_positions": int(current_value * 0.1 / default_per_trade) if current_value > 0 else 0,
            "investment_efficiency": (avg_investment_per_etf / default_per_trade) * 100 if default_per_trade > 0 else 0
        }


def main():
    """Main function for investment manager testing"""
    print("💰 Investment Manager")
    print("=" * 25)
    
    from etf_data_manager import ETFDataManager
    
    # Initialize
    data_manager = ETFDataManager()
    investment_manager = InvestmentManager(data_manager)
    
    # Run interactive setup
    investment_manager.interactive_investment_setup()


if __name__ == "__main__":
    main()