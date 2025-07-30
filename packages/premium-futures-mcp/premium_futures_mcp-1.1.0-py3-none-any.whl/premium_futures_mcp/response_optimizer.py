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
        
        # Debug information
        debug_info = {
            "input_type": type(balance_data).__name__,
            "input_length": len(balance_data) if isinstance(balance_data, list) else 0,
            "sample_entries": [],
            "processing_errors": []
        }
        
        if not isinstance(balance_data, list):
            return {
                "error": "Expected list but got " + str(type(balance_data)),
                "debug": debug_info,
                "raw_data": balance_data
            }
        
        for i, bal in enumerate(balance_data):
            if i < 3:  # Store first 3 entries for debugging
                debug_info["sample_entries"].append(bal)
                
            try:
                # Validate that bal is a dict-like object
                if not isinstance(bal, dict) and not hasattr(bal, 'get'):
                    debug_info["processing_errors"].append({
                        "index": i,
                        "error": f"Item is not dict-like, got {type(bal)}",
                        "item": str(bal)
                    })
                    continue
                
                # Safely extract values with multiple fallbacks
                def safe_float_extract(obj, key, default=0):
                    """Safely extract and convert to float"""
                    try:
                        if hasattr(obj, 'get'):
                            value = obj.get(key, default)
                        elif isinstance(obj, dict):
                            value = obj.get(key, default)
                        else:
                            return default
                        
                        if value is None or value == "":
                            return default
                        return float(value)
                    except (ValueError, TypeError, AttributeError):
                        return default
                
                def safe_string_extract(obj, key, default=""):
                    """Safely extract string value"""
                    try:
                        if hasattr(obj, 'get'):
                            value = obj.get(key, default)
                        elif isinstance(obj, dict):
                            value = obj.get(key, default)
                        else:
                            return default
                        return str(value) if value is not None else default
                    except (AttributeError, TypeError):
                        return default
                
                # Extract values safely using correct field names for /fapi/v3/balance endpoint
                # Primary fields from Balance V3 endpoint
                wallet_balance = safe_float_extract(bal, "balance", 0)  # Main balance field
                unrealized_pnl = safe_float_extract(bal, "crossUnPnl", 0)  # Cross unrealized PnL
                available_balance = safe_float_extract(bal, "availableBalance", 0)
                cross_wallet_balance = safe_float_extract(bal, "crossWalletBalance", 0)
                max_withdraw = safe_float_extract(bal, "maxWithdrawAmount", 0)
                
                # Fallback to Account Info V3 field names (in case this optimizer is used for account endpoint)
                if wallet_balance == 0:
                    wallet_balance = safe_float_extract(bal, "walletBalance", 0)  # Account Info field name
                if unrealized_pnl == 0:
                    unrealized_pnl = safe_float_extract(bal, "unrealizedProfit", 0)  # Account Info field name
                
                asset_name = safe_string_extract(bal, "asset", "UNKNOWN")
                
                # Check if this balance entry has any non-zero values (including all balance fields)
                if (wallet_balance != 0 or unrealized_pnl != 0 or available_balance != 0 or 
                    cross_wallet_balance != 0 or max_withdraw != 0):
                    
                    non_zero_balances.append({
                        "asset": asset_name,
                        "balance": wallet_balance,  # Main balance
                        "cross_wallet_balance": cross_wallet_balance,
                        "unrealized_pnl": unrealized_pnl,
                        "available_balance": available_balance,
                        "max_withdraw_amount": max_withdraw
                    })
                
                total_wallet_balance += wallet_balance
                total_unrealized_pnl += unrealized_pnl
                
            except Exception as e:
                # Handle any unexpected errors
                debug_info["processing_errors"].append({
                    "index": i,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "entry": str(bal)[:200]  # Limit string length
                })
        
        result = {
            "total_wallet_balance": total_wallet_balance,
            "total_unrealized_pnl": total_unrealized_pnl,
            "assets": non_zero_balances,
            "asset_count": len(non_zero_balances)
        }
        
        # Add debug info if no assets found or if there were processing errors
        if len(non_zero_balances) == 0 or len(debug_info["processing_errors"]) > 0:
            result["debug"] = debug_info
            
        return result
    
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
