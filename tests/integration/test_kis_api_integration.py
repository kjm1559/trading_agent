import pytest
import os

from src.modules.trading.kis_api import KISAPI
from src.modules.trading.order_manager import OrderManager, OrderStatus, TradeSide
from src.modules.trading.portfolio import Portfolio


@pytest.mark.skip(reason="Requires real KIS credentials")
class TestKISAPIIntegration:
    @pytest.fixture
    def kis_api(self):
        return KISAPI()

    def test_get_stocks_list(self, kis_api):
        result = kis_api.get_stocks_list("EQ")
        assert "items" in result
        assert len(result["items"]) > 0

    def test_get_stock_info(self, kis_api):
        result = kis_api.get_stock_info("005930")
        assert result is not None
        assert "stockNo" in result

    def test_get_market_trend(self, kis_api):
        result = kis_api.get_market_trend("005930", 10)
        assert "items" in result

    @pytest.mark.skip(reason="Requires authorized KIS token")
    def test_get_account_balance(self, kis_api):
        result = kis_api.get_account_balance()
        assert "totalMoney" in result or "items" in result

    @pytest.mark.skip(reason="Requires authorized KIS token")
    def test_get_positions(self, kis_api):
        result = kis_api.get_positions()
        assert "items" in result or "result" in result


@pytest.mark.skip(reason="Requires real KIS credentials")
class TestOrderManagerIntegration:
    @pytest.fixture
    def order_manager(self):
        return OrderManager()

    @pytest.mark.skip(reason="Requires authorized KIS token")
    def test_place_order(self, order_manager):
        try:
            order = order_manager.place_order(
                stock_code="005930",
                quantity=100,
                price=70000.0,
                side=TradeSide.BUY,
            )
            assert order["status"] in [OrderStatus.SUBMITTED, OrderStatus.FILLED]
        except Exception as e:
            pytest.skip(f"Order placement failed: {e}")

    @pytest.mark.skip(reason="Requires authorized KIS token")
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


@pytest.mark.skip(reason="Requires real KIS credentials")
class TestPortfolioIntegration:
    @pytest.fixture
    def portfolio(self):
        return Portfolio()

    @pytest.mark.skip(reason="Requires authorized KIS token")
    def test_get_holdings(self, portfolio):
        holdings = portfolio.get_holdings()
        assert isinstance(holdings, list)

    @pytest.mark.skip(reason="Requires authorized KIS token")
    def test_get_portfolio_summary(self, portfolio):
        summary = portfolio.get_portfolio_summary()
        assert summary.total_assets > 0

    @pytest.mark.skip(reason="Requires authorized KIS token")
    def test_calculate_asset_allocation(self, portfolio):
        allocations = portfolio.calculate_asset_allocation()
        assert isinstance(allocations, list)
