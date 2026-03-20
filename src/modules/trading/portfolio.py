from typing import Optional, List, Dict
from dataclasses import dataclass
from src.modules.trading.kis_api import KISAPI
from src.modules.trading.order_manager import OrderManager, OrderStatus
from src.modules.data.models import Trade, TradeSide
from src.modules.data.db import get_session


@dataclass
class Holding:
    stock_code: str
    quantity: int
    avg_price: float
    market_value: float
    cost_value: float
    profit_loss: float
    profit_rate: float


@dataclass
class PortfolioSummary:
    total_market_value: float
    total_cost_value: float
    total_profit_loss: float
    total_profit_rate: float
    cash: float
    total_assets: float
    holdings: List[Dict[str, float]]


class Portfolio:
    def __init__(
        self, kis_api: Optional[KISAPI] = None, order_manager: Optional[OrderManager] = None
    ):
        self.kis_api = kis_api or KISAPI()
        self.order_manager = order_manager or OrderManager(kis_api)
        self.holdings: Dict[str, Holding] = {}

    def get_holdings(self) -> List[Dict[str, float]]:
        positions = self.kis_api.get_positions()
        items = positions.get("items", [])

        result = []
        for item in items:
            stock_code = item.get("stockNo")
            quantity = item.get("qty", 0)
            avg_price = float(item.get("avgPrice", 0))
            market_price = float(item.get("price", 0))

            market_value = quantity * market_price
            cost_value = quantity * avg_price
            profit_loss = market_value - cost_value
            profit_rate = profit_loss / cost_value * 100 if cost_value > 0 else 0

            result.append(
                {
                    "stock_code": stock_code,
                    "quantity": quantity,
                    "avg_price": avg_price,
                    "market_price": market_price,
                    "market_value": market_value,
                    "cost_value": cost_value,
                    "profit_loss": profit_loss,
                    "profit_rate": profit_rate,
                }
            )

        return result

    def get_portfolio_summary(self) -> PortfolioSummary:
        holdings_data = self.get_holdings()
        balance = self.kis_api.get_account_balance()

        total_market_value = sum(h["market_value"] for h in holdings_data)
        total_cost_value = sum(h["cost_value"] for h in holdings_data)
        total_profit_loss = sum(h["profit_loss"] for h in holdings_data)
        cash = float(balance.get("totalMoney", 0))
        total_assets = total_market_value + cash

        total_profit_rate = (
            total_profit_loss / total_cost_value * 100 if total_cost_value > 0 else 0
        )

        return PortfolioSummary(
            total_market_value=total_market_value,
            total_cost_value=total_cost_value,
            total_profit_loss=total_profit_loss,
            total_profit_rate=total_profit_rate,
            cash=cash,
            total_assets=total_assets,
            holdings=holdings_data,
        )

    def record_trade(self, trade_data: dict) -> Trade:
        with get_session() as session:
            trade = Trade(
                stock_code=trade_data["stock_code"],
                quantity=trade_data["quantity"],
                price=trade_data["price"],
                side=trade_data["side"],
            )
            session.add(trade)
        return trade

    def calculate_asset_allocation(self) -> List[Dict[str, float]]:
        summary = self.get_portfolio_summary()

        if summary.total_assets <= 0:
            return []

        allocations = []
        for holding in summary.holdings:
            allocation = holding["market_value"] / summary.total_assets * 100
            allocations.append(
                {
                    "stock_code": holding["stock_code"],
                    "market_value": holding["market_value"],
                    "allocation": allocation,
                }
            )

        return allocations

    def get_cash_percentage(self) -> float:
        summary = self.get_portfolio_summary()
        if summary.total_assets <= 0:
            return 0.0
        return summary.cash / summary.total_assets * 100

    def rebalance_portfolio(
        self,
        target_allocations: Dict[str, float],
        max_allocation_per_stock: float = 0.2,
    ) -> List[Dict]:
        summary = self.get_portfolio_summary()
        current_allocations = self.calculate_asset_allocation()

        proposed_orders = []
        
        for stock_code, target_pct in target_allocations.items():
            if target_pct > max_allocation_per_stock:
                target_pct = max_allocation_per_stock

            current_pct = next(
                (a["allocation"] for a in current_allocations if a["stock_code"] == stock_code),
                0,
            )

            if abs(target_pct - current_pct) > 0.05:
                stock_info = {}
                for holding in summary.holdings:
                    if holding["stock_code"] == stock_code:
                        stock_info = holding
                        break

                market_price = stock_info.get("market_price", 0)
                if market_price > 0:
                    if target_pct > current_pct:
                        order_val = (
                            summary.total_assets * target_pct
                            - summary.total_assets * current_pct
                        )
                        quantity = int(order_val / market_price // 100) * 100
                        if quantity > 0:
                            proposed_orders.append(
                                {
                                    "stock_code": stock_code,
                                    "quantity": quantity,
                                    "price": market_price,
                                    "side": TradeSide.BUY,
                                }
                            )
                    else:
                        order_val = (
                            summary.total_assets * current_pct
                            - summary.total_assets * target_pct
                        )
                        quantity = int(order_val / market_price // 100) * 100
                        if quantity > 0:
                            proposed_orders.append(
                                {
                                    "stock_code": stock_code,
                                    "quantity": quantity,
                                    "price": market_price,
                                    "side": TradeSide.SELL,
                                }
                            )

        return proposed_orders