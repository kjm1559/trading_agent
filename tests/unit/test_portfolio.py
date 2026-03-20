import pytest
from unittest.mock import Mock, patch, MagicMock

from src.modules.trading.portfolio import Portfolio, PortfolioSummary
from src.modules.data.models import TradeSide


class TestPortfolio:
    @pytest.fixture
    def mock_kis_api(self):
        api = MagicMock()
        api.get_positions.return_value = {
            "items": [
                {
                    "stockNo": "005930",
                    "qty": 100,
                    "avgPrice": 70000.0,
                    "price": 75000.0,
                },
                {
                    "stockNo": "000660",
                    "qty": 200,
                    "avgPrice": 240000.0,
                    "price": 250000.0,
                },
            ]
        }
        api.get_account_balance.return_value = {
            "totalMoney": 10000000,
        }
        return api

    @pytest.fixture
    def mock_order_manager(self):
        manager = MagicMock()
        return manager

    @pytest.fixture
    def portfolio(self, mock_kis_api, mock_order_manager):
        return Portfolio(mock_kis_api, mock_order_manager)

    def test_init_with_dependencies(self, mock_kis_api, mock_order_manager):
        portfolio = Portfolio(mock_kis_api, mock_order_manager)
        assert portfolio.kis_api == mock_kis_api
        assert portfolio.order_manager == mock_order_manager

    def test_init_without_dependencies(self):
        with patch("src.modules.trading.portfolio.KISAPI"):
            with patch("src.modules.trading.portfolio.OrderManager"):
                portfolio = Portfolio()
                assert portfolio.kis_api is not None
                assert portfolio.order_manager is not None

    def test_get_holdings(self, portfolio):
        holdings = portfolio.get_holdings()

        assert len(holdings) == 2
        assert holdings[0]["stock_code"] == "005930"
        assert holdings[0]["quantity"] == 100
        assert holdings[0]["avg_price"] == 70000.0
        assert holdings[0]["profit_loss"] > 0

    def test_get_holdings_empty(self, mock_kis_api, mock_order_manager):
        mock_kis_api.get_positions.return_value = {"items": []}
        portfolio = Portfolio(mock_kis_api, mock_order_manager)
        holdings = portfolio.get_holdings()
        assert len(holdings) == 0

    def test_get_portfolio_summary(self, portfolio):
        summary = portfolio.get_portfolio_summary()

        assert isinstance(summary, PortfolioSummary)
        assert summary.total_market_value > 0
        assert summary.total_cost_value > 0
        assert summary.cash == 10000000
        assert summary.total_assets > 0

    def test_get_portfolio_summary_profit(self, portfolio):
        summary = portfolio.get_portfolio_summary()

        assert summary.total_profit_loss > 0
        assert summary.total_profit_rate > 0

    def test_get_portfolio_summary_loss(
        self, mock_kis_api, mock_order_manager
    ):
        mock_kis_api.get_positions.return_value = {
            "items": [
                {
                    "stockNo": "005930",
                    "qty": 100,
                    "avgPrice": 80000.0,
                    "price": 75000.0,
                },
            ]
        }
        portfolio = Portfolio(mock_kis_api, mock_order_manager)
        summary = portfolio.get_portfolio_summary()

        assert summary.total_profit_loss < 0
        assert summary.total_profit_rate < 0

    def test_calculate_asset_allocation(self, portfolio):
        allocations = portfolio.calculate_asset_allocation()

        assert len(allocations) == 2
        for alloc in allocations:
            assert "stock_code" in alloc
            assert "market_value" in alloc
            assert "allocation" in alloc
            assert 0 <= alloc["allocation"] <= 100

    def test_calculate_asset_allocation_empty(self, mock_kis_api, mock_order_manager):
        mock_kis_api.get_positions.return_value = {"items": []}
        portfolio = Portfolio(mock_kis_api, mock_order_manager)
        allocations = portfolio.calculate_asset_allocation()

        assert len(allocations) == 0

    def test_calculate_asset_allocation_zero_assets(
        self, mock_kis_api, mock_order_manager
    ):
        mock_kis_api.get_positions.return_value = {"items": []}
        mock_kis_api.get_account_balance.return_value = {"totalMoney": 0}
        portfolio = Portfolio(mock_kis_api, mock_order_manager)
        allocations = portfolio.calculate_asset_allocation()
        assert len(allocations) == 0

    def test_get_cash_percentage(self, portfolio):
        cash_pct = portfolio.get_cash_percentage()

        assert 0 <= cash_pct <= 100

    def test_rebalance_portfolio_no_change(self, portfolio):
        target_allocations = {"005930": 0.1, "000660": 0.1}
        proposed_orders = portfolio.rebalance_portfolio(target_allocations)

        for order in proposed_orders:
            assert "stock_code" in order
            assert "quantity" in order
            assert "price" in order
            assert "side" in order

    def test_rebalance_portfolio_buy(self, portfolio):
        target_allocations = {"005930": 0.5}
        proposed_orders = portfolio.rebalance_portfolio(target_allocations)

        for order in proposed_orders:
            if order["side"] == TradeSide.BUY:
                assert order["quantity"] > 0
                break

    def test_rebalance_portfolio_sell(self, portfolio):
        target_allocations = {"005930": 0.0, "000660": 0.0}
        proposed_orders = portfolio.rebalance_portfolio(target_allocations)

        sell_orders = [o for o in proposed_orders if o["side"] == TradeSide.SELL]
        assert len(sell_orders) > 0

    def test_rebalance_portfolio_max_allocation(self, portfolio):
        target_allocations = {"005930": 0.5}
        proposed_orders = portfolio.rebalance_portfolio(
            target_allocations, max_allocation_per_stock=0.1
        )

        for order in proposed_orders:
            if order["side"] == TradeSide.BUY:
                assert order["quantity"] > 0
                break