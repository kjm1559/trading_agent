import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.modules.trading.order_manager import OrderManager, OrderStatus
from src.modules.data.models import TradeSide


class TestOrderManager:
    @pytest.fixture
    def mock_kis_api(self):
        api = MagicMock()
        api.submit_order.return_value = {"orderKey": "order_123"}
        api.cancel_order.return_value = {"status": "success"}
        api.get_market_data.return_value = {"data": "market_data"}
        return api

    @pytest.fixture
    def order_manager(self, mock_kis_api):
        return OrderManager(mock_kis_api)

    def test_init_with_kis_api(self, mock_kis_api):
        manager = OrderManager(mock_kis_api)
        assert manager.kis_api == mock_kis_api
        assert manager.pending_orders == {}

    def test_init_without_kis_api(self):
        with patch("src.modules.trading.order_manager.KISAPI"):
            manager = OrderManager()
            assert manager.kis_api is not None

    def test_create_order(self, order_manager):
        order = order_manager.create_order(
            stock_code="005930",
            quantity=100,
            price=70000.0,
            side=TradeSide.BUY,
        )

        assert order["stock_code"] == "005930"
        assert order["quantity"] == 100
        assert order["price"] == 70000.0
        assert order["side"] == TradeSide.BUY
        assert order["status"] == OrderStatus.PENDING

    def test_create_order_unique_key(self, order_manager):
        order1 = order_manager.create_order(
            stock_code="005930",
            quantity=100,
            price=70000.0,
            side=TradeSide.BUY,
        )
        import time as time_module
        time_module.sleep(0.01)
        order2 = order_manager.create_order(
            stock_code="005930",
            quantity=100,
            price=70000.0,
            side=TradeSide.BUY,
        )

        assert order1["order_key"] != order2["order_key"]

    def test_submit_order(self, order_manager):
        order = order_manager.create_order(
            stock_code="005930",
            quantity=100,
            price=70000.0,
            side=TradeSide.BUY,
        )
        result = order_manager.submit_order(order)

        assert result["status"] == OrderStatus.SUBMITTED
        assert result.get("submitted_at") is not None
        assert result.get("external_order_key") == "order_123"

    def test_cancel_order(self, order_manager):
        order = order_manager.create_order(
            stock_code="005930",
            quantity=100,
            price=70000.0,
            side=TradeSide.BUY,
        )
        order = order_manager.submit_order(order)
        result = order_manager.cancel_order(order["order_key"])

        assert result["status"] == OrderStatus.CANCELLED
        assert result.get("cancelled_at") is not None
        assert order_manager.kis_api.cancel_order.called

    def test_cancel_order_not_found(self, order_manager):
        with pytest.raises(ValueError):
            order_manager.cancel_order("nonexistent")

    def test_get_order(self, order_manager):
        order = order_manager.create_order(
            stock_code="005930",
            quantity=100,
            price=70000.0,
            side=TradeSide.BUY,
        )
        result = order_manager.get_order(order["order_key"])

        assert result is not None
        assert result["stock_code"] == "005930"

    def test_get_order_not_found(self, order_manager):
        result = order_manager.get_order("nonexistent")
        assert result is None

    def test_get_pending_orders(self, order_manager):
        order1 = order_manager.create_order(
            stock_code="005930",
            quantity=100,
            price=70000.0,
            side=TradeSide.BUY,
        )
        order2 = order_manager.create_order(
            stock_code="000660",
            quantity=100,
            price=240000.0,
            side=TradeSide.BUY,
        )
        order_manager.update_order_status(order2["order_key"], OrderStatus.CANCELLED)

        pending = order_manager.get_pending_orders()
        assert len(pending) == 1
        assert pending[0]["order_key"] == order1["order_key"]

    def test_get_all_orders(self, order_manager):
        order1 = order_manager.create_order(
            stock_code="005930",
            quantity=100,
            price=70000.0,
            side=TradeSide.BUY,
        )
        order2 = order_manager.create_order(
            stock_code="000660",
            quantity=100,
            price=240000.0,
            side=TradeSide.BUY,
        )

        orders = order_manager.get_all_orders()
        assert len(orders) == 2

    def test_update_order_status(self, order_manager):
        order = order_manager.create_order(
            stock_code="005930",
            quantity=100,
            price=70000.0,
            side=TradeSide.BUY,
        )
        result = order_manager.update_order_status(
            order["order_key"],
            OrderStatus.FILLED,
            filled_at=datetime.now(),
        )

        assert result["status"] == OrderStatus.FILLED
        assert result["filled_at"] is not None

    def test_update_order_status_not_found(self, order_manager):
        with pytest.raises(ValueError):
            order_manager.update_order_status("nonexistent", OrderStatus.CANCELLED)

    def test_calculate_order_value(self, order_manager):
        result = order_manager.calculate_order_value(100, 70000.0)
        assert result == 7000000.0

    def test_validate_order_valid(self, order_manager):
        is_valid, message = order_manager.validate_order(
            stock_code="005930",
            quantity=100,
            price=70000.0,
        )

        assert is_valid is True
        assert message == "Order is valid"

    def test_validate_order_invalid_stock_code(self, order_manager):
        is_valid, message = order_manager.validate_order(
            stock_code="0059",
            quantity=100,
            price=70000.0,
        )

        assert is_valid is False

    def test_validate_order_invalid_quantity(self, order_manager):
        is_valid, message = order_manager.validate_order(
            stock_code="005930",
            quantity=50,
            price=70000.0,
        )

        assert is_valid is False

    def test_validate_order_invalid_price(self, order_manager):
        is_valid, message = order_manager.validate_order(
            stock_code="005930",
            quantity=100,
            price=-100.0,
        )

        assert is_valid is False

    def test_place_order_valid(self, order_manager):
        order = order_manager.place_order(
            stock_code="005930",
            quantity=100,
            price=70000.0,
            side=TradeSide.BUY,
        )

        assert order["status"] == OrderStatus.SUBMITTED

    def test_place_order_invalid(self, order_manager):
        with pytest.raises(ValueError):
            order_manager.place_order(
                stock_code="005930",
                quantity=50,
                price=70000.0,
                side=TradeSide.BUY,
            )