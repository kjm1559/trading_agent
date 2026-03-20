from enum import Enum
from typing import Optional, List
from datetime import datetime, timedelta
import time

from src.modules.trading.kis_api import KISAPI
from src.modules.data.models import Trade, TradeSide, MarketData
from src.modules.data.db import get_session


class OrderStatus(str, Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class OrderManager:
    def __init__(self, kis_api: Optional[KISAPI] = None):
        self.kis_api = kis_api or KISAPI()
        self.pending_orders: dict[str, dict] = {}

    def create_order(
        self,
        stock_code: str,
        quantity: int,
        price: float,
        side: TradeSide,
    ) -> dict:
        order_key = self._generate_order_key(stock_code, side, price)
        order = {
            "order_key": order_key,
            "stock_code": stock_code,
            "quantity": quantity,
            "price": price,
            "side": side,
            "status": OrderStatus.PENDING,
            "created_at": datetime.now(),
            "filled_at": None,
        }
        self.pending_orders[order_key] = order
        return order

    def _generate_order_key(
        self, stock_code: str, side: TradeSide, price: float
    ) -> str:
        timestamp = int(time.time() * 1000)
        return f"{stock_code}_{side.value}_{price}_{timestamp}"

    def submit_order(self, order: dict) -> dict:
        order["status"] = OrderStatus.SUBMITTED
        order["submitted_at"] = datetime.now()

        response = self.kis_api.submit_order(
            stock_code=order["stock_code"],
            quantity=order["quantity"],
            price=order["price"],
            order_type=order["side"].value,
        )
        order["external_order_key"] = response.get("orderKey")

        return order

    def cancel_order(self, order_key: str) -> dict:
        if order_key not in self.pending_orders:
            raise ValueError(f"Order {order_key} not found")

        order = self.pending_orders[order_key]
        order["status"] = OrderStatus.CANCELLED
        order["cancelled_at"] = datetime.now()

        if order.get("external_order_key"):
            self.kis_api.cancel_order(order["external_order_key"])

        return order

    def get_order(self, order_key: str) -> Optional[dict]:
        return self.pending_orders.get(order_key)

    def get_pending_orders(self) -> List[dict]:
        return [
            order
            for order in self.pending_orders.values()
            if order["status"] == OrderStatus.PENDING
        ]

    def get_all_orders(self) -> List[dict]:
        return list(self.pending_orders.values())

    def record_trade(self, order: dict) -> Trade:
        with get_session() as session:
            trade = Trade(
                stock_code=order["stock_code"],
                quantity=order["quantity"],
                price=order["price"],
                side=order["side"],
                timestamp=order["created_at"],
            )
            session.add(trade)
        return trade

    def update_order_status(
        self, order_key: str, status: OrderStatus, filled_at: Optional[datetime] = None
    ) -> dict:
        if order_key not in self.pending_orders:
            raise ValueError(f"Order {order_key} not found")

        order = self.pending_orders[order_key]
        order["status"] = status
        if filled_at:
            order["filled_at"] = filled_at

        return order

    def calculate_order_value(self, quantity: int, price: float) -> float:
        return quantity * price

    def validate_order(
        self, stock_code: str, quantity: int, price: float
    ) -> tuple[bool, str]:
        if not stock_code or len(stock_code) != 6:
            return False, "Invalid stock code"
        if quantity <= 0:
            return False, "Quantity must be positive"
        if quantity % 100 != 0:
            return False, "Quantity must be multiple of 100"
        if price <= 0:
            return False, "Price must be positive"

        market_data = self.kis_api.get_market_data(stock_code)
        if not market_data:
            return False, "Stock not found"

        return True, "Order is valid"

    def place_order(
        self,
        stock_code: str,
        quantity: int,
        price: float,
        side: TradeSide,
    ) -> dict:
        is_valid, message = self.validate_order(stock_code, quantity, price)
        if not is_valid:
            raise ValueError(f"Invalid order: {message}")

        order = self.create_order(stock_code, quantity, price, side)
        order = self.submit_order(order)
        return order
