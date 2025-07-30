#!/usr/bin/env python3
"""
Response Optimizer for reducing token usage in MCP responses
"""

from typing import Any, Dict, List
from decimal import Decimal

class ResponseOptimizer:
    """Optimizes API responses to reduce token consumption"""
    
    @staticmethod
    def optimize_positions(positions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize position data by removing unnecessary fields and formatting"""
        optimized = []
        for pos in positions:
            # Only include essential fields
            optimized_pos = {
                "symbol": pos.get("symbol"),
                "size": float(pos.get("positionAmt", 0)),
                "side": "LONG" if float(pos.get("positionAmt", 0)) > 0 else "SHORT",
                "entry_price": float(pos.get("entryPrice", 0)),
                "mark_price": float(pos.get("markPrice", 0)),
                "pnl": float(pos.get("unRealizedProfit", 0)),
                "pnl_pct": float(pos.get("percentage", 0)) if pos.get("percentage") else 0,
                "margin": float(pos.get("initialMargin", 0)),
                "leverage": int(float(pos.get("leverage", 1)))
            }
            optimized.append(optimized_pos)
        return optimized
    
    @staticmethod
    def optimize_orders(orders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize order data"""
        optimized = []
        for order in orders:
            optimized_order = {
                "id": order.get("orderId"),
                "symbol": order.get("symbol"),
                "side": order.get("side"),
                "type": order.get("type"),
                "qty": float(order.get("origQty", 0)),
                "price": float(order.get("price", 0)),
                "status": order.get("status"),
                "time": order.get("time")
            }
            optimized.append(optimized_order)
        return optimized
    
    @staticmethod
    def optimize_balance(balance_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Optimize balance data to show only non-zero balances"""
        non_zero_balances = []
        total_wallet_balance = 0
        total_unrealized_pnl = 0
        
        for bal in balance_data:
            wallet_balance = float(bal.get("walletBalance", 0))
            unrealized_pnl = float(bal.get("unrealizedProfit", 0))
            
            if wallet_balance != 0 or unrealized_pnl != 0:
                non_zero_balances.append({
                    "asset": bal.get("asset"),
                    "wallet_balance": wallet_balance,
                    "unrealized_pnl": unrealized_pnl,
                    "available": float(bal.get("availableBalance", 0))
                })
            
            total_wallet_balance += wallet_balance
            total_unrealized_pnl += unrealized_pnl
        
        return {
            "total_wallet_balance": total_wallet_balance,
            "total_unrealized_pnl": total_unrealized_pnl,
            "assets": non_zero_balances,
            "asset_count": len(non_zero_balances)
        }
    
    @staticmethod
    def optimize_ticker_data(tickers: List[Dict[str, Any]], limit: int = 20) -> List[Dict[str, Any]]:
        """Optimize ticker data for top movers"""
        optimized = []
        for ticker in tickers[:limit]:
            optimized_ticker = {
                "symbol": ticker.get("symbol"),
                "price": float(ticker.get("lastPrice", 0)),
                "change": float(ticker.get("priceChange", 0)),
                "change_pct": float(ticker.get("priceChangePercent", 0)),
                "volume": float(ticker.get("volume", 0))
            }
            optimized.append(optimized_ticker)
        return optimized
