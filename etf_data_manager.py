import json
import pandas as pd
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
import requests

class ETFDataManager:
    """Manages ETF data, prices, and portfolio with JSON storage"""
    
    def __init__(self, data_file: str = "etf_data.json"):
        self.data_file = data_file
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load data from JSON file or create default structure"""
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "etfs": {},
                "portfolio": [],
                "transactions": [],
                "last_updated": None
            }
    
    def _save_data(self):
        """Save data to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2, default=str)
    
    def load_etf_list_from_excel(self, excel_file: str) -> List[str]:
        """Load ETF names from Excel file"""
        df = pd.read_excel(excel_file)
        # Assuming the first column contains ETF names
        etf_names = df.iloc[:, 0].tolist()
        
        # Initialize ETF data structure if not exists
        for etf_name in etf_names:
            if etf_name not in self.data["etfs"]:
                self.data["etfs"][etf_name] = {
                    "name": etf_name,
                    "cmp": None,
                    "dma_20": None,
                    "last_price_update": None,
                    "deviation_percent": None
                }
        
        self._save_data()
        return etf_names
    
    def update_etf_price(self, etf_name: str, cmp: float, dma_20: float):
        """Update ETF current market price and 20-day moving average"""
        if etf_name not in self.data["etfs"]:
            self.data["etfs"][etf_name] = {"name": etf_name}
        
        # Calculate deviation percentage
        deviation_percent = ((cmp - dma_20) / dma_20) * 100
        
        self.data["etfs"][etf_name].update({
            "cmp": cmp,
            "dma_20": dma_20,
            "last_price_update": datetime.now().isoformat(),
            "deviation_percent": deviation_percent
        })
        
        self._save_data()
    
    def get_etf_rankings(self) -> List[Tuple[str, float, float, float]]:
        """Get ETFs ranked by deviation from 20-day moving average (ascending)"""
        rankings = []
        
        for etf_name, etf_data in self.data["etfs"].items():
            if etf_data.get("cmp") and etf_data.get("dma_20"):
                deviation = etf_data["deviation_percent"]
                rankings.append((
                    etf_name, 
                    etf_data["cmp"], 
                    etf_data["dma_20"], 
                    deviation
                ))
        
        # Sort by deviation (ascending - most fallen first)
        rankings.sort(key=lambda x: x[3])
        return rankings
    
    def get_current_holdings(self) -> Dict[str, List[Dict]]:
        """Get current portfolio holdings grouped by ETF"""
        holdings = {}
        
        for holding in self.data["portfolio"]:
            if holding["status"] == "active":
                etf_name = holding["etf_name"]
                if etf_name not in holdings:
                    holdings[etf_name] = []
                holdings[etf_name].append(holding)
        
        return holdings
    
    def add_purchase(self, etf_name: str, quantity: int, price: float, date_str: str = None):
        """Add a purchase transaction"""
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        transaction = {
            "id": len(self.data["portfolio"]) + 1,
            "etf_name": etf_name,
            "type": "buy",
            "quantity": quantity,
            "price": price,
            "date": date_str,
            "status": "active",
            "total_amount": quantity * price
        }
        
        self.data["portfolio"].append(transaction)
        self.data["transactions"].append(transaction.copy())
        self._save_data()
        
        return transaction["id"]
    
    def sell_holding_lifo(self, etf_name: str, quantity: int, price: float, date_str: str = None) -> Optional[Dict]:
        """Sell holdings using LIFO (Last In First Out) method"""
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        # Get active holdings for this ETF, sorted by date (newest first for LIFO)
        active_holdings = [h for h in self.data["portfolio"] 
                          if h["etf_name"] == etf_name and h["status"] == "active"]
        active_holdings.sort(key=lambda x: x["date"], reverse=True)
        
        if not active_holdings:
            return None
        
        # Use the most recent holding (LIFO)
        holding_to_sell = active_holdings[0]
        
        if holding_to_sell["quantity"] < quantity:
            quantity = holding_to_sell["quantity"]  # Can't sell more than we have
        
        # Calculate profit
        buy_price = holding_to_sell["price"]
        profit_per_unit = price - buy_price
        total_profit = profit_per_unit * quantity
        profit_percent = (profit_per_unit / buy_price) * 100
        
        # Create sell transaction
        sell_transaction = {
            "id": len(self.data["transactions"]) + 1,
            "etf_name": etf_name,
            "type": "sell",
            "quantity": quantity,
            "price": price,
            "date": date_str,
            "buy_price": buy_price,
            "profit_per_unit": profit_per_unit,
            "total_profit": total_profit,
            "profit_percent": profit_percent,
            "total_amount": quantity * price,
            "linked_buy_id": holding_to_sell["id"]
        }
        
        # Update holding quantity or mark as sold
        if holding_to_sell["quantity"] == quantity:
            holding_to_sell["status"] = "sold"
        else:
            holding_to_sell["quantity"] -= quantity
        
        self.data["transactions"].append(sell_transaction)
        self._save_data()
        
        return sell_transaction
    
    def get_etfs_for_averaging(self, loss_threshold: float = -2.5) -> List[Tuple[str, float, float]]:
        """Get ETFs that are suitable for averaging down (below loss threshold)"""
        current_holdings = self.get_current_holdings()
        averaging_candidates = []
        
        for etf_name, holdings in current_holdings.items():
            if etf_name in self.data["etfs"]:
                current_price = self.data["etfs"][etf_name].get("cmp")
                if current_price:
                    # Calculate average purchase price
                    total_cost = sum(h["quantity"] * h["price"] for h in holdings)
                    total_quantity = sum(h["quantity"] for h in holdings)
                    avg_buy_price = total_cost / total_quantity
                    
                    # Calculate current loss percentage
                    loss_percent = ((current_price - avg_buy_price) / avg_buy_price) * 100
                    
                    if loss_percent <= loss_threshold:
                        averaging_candidates.append((etf_name, loss_percent, current_price))
        
        # Sort by loss percentage (most loss first)
        averaging_candidates.sort(key=lambda x: x[1])
        return averaging_candidates
    
    def get_etfs_for_selling(self, profit_threshold: float = 6.0) -> List[Tuple[str, float, float, Dict]]:
        """Get ETFs that meet the selling criteria (above profit threshold)"""
        current_holdings = self.get_current_holdings()
        selling_candidates = []
        
        for etf_name, holdings in current_holdings.items():
            if etf_name in self.data["etfs"]:
                current_price = self.data["etfs"][etf_name].get("cmp")
                if current_price:
                    # Check each holding for profit (LIFO - most recent first)
                    holdings.sort(key=lambda x: x["date"], reverse=True)
                    for holding in holdings:
                        profit_percent = ((current_price - holding["price"]) / holding["price"]) * 100
                        if profit_percent >= profit_threshold:
                            selling_candidates.append((
                                etf_name, 
                                profit_percent, 
                                current_price,
                                holding
                            ))
                            break  # Only consider the most recent holding (LIFO)
        
        # Sort by profit percentage (highest profit first)
        selling_candidates.sort(key=lambda x: x[1], reverse=True)
        return selling_candidates
    
    def get_portfolio_summary(self) -> Dict:
        """Get portfolio summary with current values"""
        holdings = self.get_current_holdings()
        summary = {
            "total_etfs": len(holdings),
            "total_investments": 0,
            "current_value": 0,
            "total_profit_loss": 0,
            "holdings_detail": []
        }
        
        for etf_name, etf_holdings in holdings.items():
            total_quantity = sum(h["quantity"] for h in etf_holdings)
            total_cost = sum(h["quantity"] * h["price"] for h in etf_holdings)
            avg_buy_price = total_cost / total_quantity
            
            current_price = self.data["etfs"][etf_name].get("cmp", 0)
            current_value = total_quantity * current_price
            profit_loss = current_value - total_cost
            profit_loss_percent = (profit_loss / total_cost) * 100 if total_cost > 0 else 0
            
            summary["total_investments"] += total_cost
            summary["current_value"] += current_value
            summary["total_profit_loss"] += profit_loss
            
            summary["holdings_detail"].append({
                "etf_name": etf_name,
                "quantity": total_quantity,
                "avg_buy_price": round(avg_buy_price, 2),
                "current_price": current_price,
                "total_cost": round(total_cost, 2),
                "current_value": round(current_value, 2),
                "profit_loss": round(profit_loss, 2),
                "profit_loss_percent": round(profit_loss_percent, 2)
            })
        
        return summary