from etf_data_manager import ETFDataManager
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class ETFTradingStrategy:
    """Implements the ETF trading strategy logic"""
    
    def __init__(self, data_manager: ETFDataManager, volume_filter=None):
        self.data_manager = data_manager
        self.volume_filter = volume_filter
        self.max_rank_to_consider = 5  # Top 5 ETFs to consider
        self.averaging_loss_threshold = -2.5  # 2.5% loss threshold for averaging
        self.profit_threshold = 6.0  # 6% profit threshold for selling
        self.max_daily_transactions = 1  # Max 1 buy and 1 sell per day
        self.volume_filtering_enabled = True  # Enable volume filtering by default
    
    def get_buy_recommendation(self) -> Optional[Dict]:
        """Get buy recommendation based on strategy rules"""
        rankings = self.data_manager.get_etf_rankings()
        current_holdings = self.data_manager.get_current_holdings()
        
        if not rankings:
            return {
                "action": "no_action",
                "reason": "No ETF data available for ranking"
            }
        
        # Filter rankings by volume qualification if enabled
        if self.volume_filtering_enabled and self.volume_filter:
            qualified_etfs = set(self.volume_filter.get_qualified_etfs())
            volume_filtered_rankings = [
                (etf_name, cmp, dma_20, deviation) 
                for etf_name, cmp, dma_20, deviation in rankings 
                if etf_name in qualified_etfs
            ]
            
            if not volume_filtered_rankings:
                return {
                    "action": "no_action",
                    "reason": "No volume-qualified ETFs available for trading"
                }
            
            rankings = volume_filtered_rankings
            
        # Alternative volume filtering using ETF data if no volume_filter object
        elif self.volume_filtering_enabled and not self.volume_filter:
            volume_filtered_rankings = []
            for etf_name, cmp, dma_20, deviation in rankings:
                etf_data = self.data_manager.data["etfs"].get(etf_name, {})
                is_volume_qualified = etf_data.get("volume_qualified", True)  # Default to True if not checked
                
                if is_volume_qualified:
                    volume_filtered_rankings.append((etf_name, cmp, dma_20, deviation))
            
            if not volume_filtered_rankings:
                return {
                    "action": "no_action",
                    "reason": "No volume-qualified ETFs meet minimum volume threshold (>50,000)"
                }
            
            rankings = volume_filtered_rankings
        
        # Get top ranked ETFs (after volume filtering)
        top_etfs = rankings[:self.max_rank_to_consider]
        held_etf_names = set(current_holdings.keys())
        
        # Rule 1: Find new ETF (not currently held) with highest rank
        for rank, (etf_name, cmp, dma_20, deviation) in enumerate(top_etfs, 1):
            if etf_name not in held_etf_names:
                return {
                    "action": "buy_new",
                    "etf_name": etf_name,
                    "rank": rank,
                    "cmp": cmp,
                    "dma_20": dma_20,
                    "deviation_percent": deviation,
                    "reason": f"New ETF at rank {rank}, deviation: {deviation:.2f}%"
                }
        
        # Rule 2: All top ETFs are held, check for averaging down
        averaging_candidates = self.data_manager.get_etfs_for_averaging(self.averaging_loss_threshold)
        
        if averaging_candidates:
            etf_name, loss_percent, current_price = averaging_candidates[0]
            return {
                "action": "average_down",
                "etf_name": etf_name,
                "current_price": current_price,
                "loss_percent": loss_percent,
                "reason": f"Average down on {etf_name}, current loss: {loss_percent:.2f}%"
            }
        
        # Rule 3: No buying opportunity
        return {
            "action": "no_action",
            "reason": "All top ETFs are held and none qualify for averaging down"
        }
    
    def get_sell_recommendation(self) -> Optional[Dict]:
        """Get sell recommendation based on profit threshold"""
        selling_candidates = self.data_manager.get_etfs_for_selling(self.profit_threshold)
        
        if selling_candidates:
            etf_name, profit_percent, current_price, holding = selling_candidates[0]
            return {
                "action": "sell",
                "etf_name": etf_name,
                "current_price": current_price,
                "profit_percent": profit_percent,
                "holding": holding,
                "reason": f"Sell {etf_name} with {profit_percent:.2f}% profit (LIFO)"
            }
        
        return {
            "action": "no_action",
            "reason": "No holdings meet the profit threshold for selling"
        }
    
    def get_daily_recommendations(self) -> Dict:
        """Get comprehensive daily trading recommendations"""
        buy_rec = self.get_buy_recommendation()
        sell_rec = self.get_sell_recommendation()
        
        # Get portfolio summary
        portfolio_summary = self.data_manager.get_portfolio_summary()
        
        # Get current rankings for display
        rankings = self.data_manager.get_etf_rankings()
        top_10_rankings = rankings[:10] if len(rankings) >= 10 else rankings
        
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "buy_recommendation": buy_rec,
            "sell_recommendation": sell_rec,
            "portfolio_summary": portfolio_summary,
            "top_etf_rankings": top_10_rankings,
            "held_etfs": list(self.data_manager.get_current_holdings().keys())
        }
    
    def execute_buy_recommendation(self, recommendation: Dict, quantity: int, actual_price: float) -> Dict:
        """Execute a buy recommendation with user-provided quantity and price"""
        if recommendation["action"] not in ["buy_new", "average_down"]:
            return {
                "success": False,
                "message": "Invalid buy recommendation"
            }
        
        etf_name = recommendation["etf_name"]
        
        try:
            transaction_id = self.data_manager.add_purchase(
                etf_name=etf_name,
                quantity=quantity,
                price=actual_price
            )
            
            return {
                "success": True,
                "transaction_id": transaction_id,
                "message": f"Successfully bought {quantity} units of {etf_name} at ₹{actual_price:.2f}",
                "total_amount": quantity * actual_price,
                "action_type": recommendation["action"]
            }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"Error executing buy: {str(e)}"
            }
    
    def execute_sell_recommendation(self, recommendation: Dict, quantity: int, actual_price: float) -> Dict:
        """Execute a sell recommendation with user-provided quantity and price"""
        if recommendation["action"] != "sell":
            return {
                "success": False,
                "message": "Invalid sell recommendation"
            }
        
        etf_name = recommendation["etf_name"]
        
        try:
            sell_transaction = self.data_manager.sell_holding_lifo(
                etf_name=etf_name,
                quantity=quantity,
                price=actual_price
            )
            
            if sell_transaction:
                return {
                    "success": True,
                    "transaction": sell_transaction,
                    "message": f"Successfully sold {quantity} units of {etf_name} at ₹{actual_price:.2f}",
                    "profit": sell_transaction["total_profit"],
                    "profit_percent": sell_transaction["profit_percent"]
                }
            else:
                return {
                    "success": False,
                    "message": f"No holdings found for {etf_name}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"Error executing sell: {str(e)}"
            }
    
    def validate_transaction_inputs(self, quantity: int, price: float) -> Tuple[bool, str]:
        """Validate user inputs for transactions"""
        if quantity <= 0:
            return False, "Quantity must be greater than 0"
        
        if price <= 0:
            return False, "Price must be greater than 0"
        
        if quantity > 10000:  # Reasonable limit
            return False, "Quantity seems too high (max 10,000)"
        
        if price > 100000:  # Reasonable limit for ETF price
            return False, "Price seems too high (max ₹1,00,000)"
        
        return True, "Valid inputs"
    
    def get_strategy_statistics(self) -> Dict:
        """Get strategy performance statistics"""
        transactions = self.data_manager.data.get("transactions", [])
        
        total_buys = len([t for t in transactions if t["type"] == "buy"])
        total_sells = len([t for t in transactions if t["type"] == "sell"])
        
        profitable_sells = [t for t in transactions if t["type"] == "sell" and t.get("total_profit", 0) > 0]
        loss_sells = [t for t in transactions if t["type"] == "sell" and t.get("total_profit", 0) <= 0]
        
        total_profit = sum(t.get("total_profit", 0) for t in transactions if t["type"] == "sell")
        win_rate = (len(profitable_sells) / total_sells * 100) if total_sells > 0 else 0
        
        return {
            "total_buy_transactions": total_buys,
            "total_sell_transactions": total_sells,
            "profitable_sells": len(profitable_sells),
            "loss_sells": len(loss_sells),
            "win_rate_percent": round(win_rate, 2),
            "total_realized_profit": round(total_profit, 2),
            "average_profit_per_sell": round(total_profit / total_sells, 2) if total_sells > 0 else 0
        }