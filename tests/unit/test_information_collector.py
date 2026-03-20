import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.modules.data.information_collector import (
    InformationCollector,
    CollectedData,
)


class TestInformationCollector:
    @pytest.fixture
    def mock_kis_api(self):
        api = MagicMock()
        api.get_market_data.return_value = {
            "stockNo": "005930",
            "price": 75000.0,
            "changePrice": 5000.0,
            "changeRate": 5.0,
            "volume": 1000000,
        }
        api.get_stock_info.return_value = {
            "stockNo": "005930",
            "stockNm": "Samsung",
            "marketType": "KOSPI",
        }
        api.get_market_trend.return_value = {
            "items": [
                {"stockNo": "005930", "price": 75000.0},
                {"stockNo": "005930", "price": 74000.0},
            ]
        }
        api.get_account_balance.return_value = {"totalMoney": 10000000}
        api.get_positions.return_value = {
            "items": [
                {
                    "stockNo": "005930",
                    "qty": 100,
                    "avgPrice": 70000.0,
                    "price": 75000.0,
                }
            ]
        }
        return api

    @pytest.fixture
    def mock_order_manager(self):
        manager = MagicMock()
        return manager

    @pytest.fixture
    def mock_portfolio(self):
        portfolio = MagicMock()
        portfolio.get_portfolio_summary.return_value = MagicMock(
            total_market_value=7500000,
            total_cost_value=7000000,
            total_profit_loss=500000,
            total_profit_rate=7.14,
            cash=10000000,
            total_assets=17500000,
            holdings=[],
        )
        return portfolio

    @pytest.fixture
    def collector(self, mock_kis_api, mock_order_manager, mock_portfolio):
        return InformationCollector(mock_kis_api, mock_order_manager, mock_portfolio)

    def test_init_with_dependencies(self, mock_kis_api, mock_order_manager, mock_portfolio):
        collector = InformationCollector(mock_kis_api, mock_order_manager, mock_portfolio)
        assert collector.kis_api == mock_kis_api
        assert collector.order_manager == mock_order_manager
        assert collector.portfolio == mock_portfolio
        assert collector.collected_data == []

    def test_init_without_dependencies(self):
        with patch(
            "src.modules.data.information_collector.KISAPI"
        ), patch("src.modules.data.information_collector.OrderManager"), patch(
            "src.modules.data.information_collector.Portfolio"
        ):
            collector = InformationCollector()
            assert collector.kis_api is not None
            assert collector.order_manager is not None
            assert collector.portfolio is not None

    def test_collect_market_data(self, collector):
        results = collector.collect_market_data(["005930"])

        assert len(results) == 1
        assert isinstance(results[0], CollectedData)
        assert results[0].stock_code == "005930"
        assert results[0].market_data.get("price") == 75000.0

    def test_collect_market_data_multiple_stocks(self, collector):
        results = collector.collect_market_data(["005930", "000660"])

        assert len(results) == 2

    def test_collect_market_data_empty(self, mock_kis_api, mock_order_manager, mock_portfolio):
        mock_kis_api.get_market_data.return_value = None
        collector = InformationCollector(mock_kis_api, mock_order_manager, mock_portfolio)
        results = collector.collect_market_data(["005930"])

        assert len(results) == 0

    def test_collect_portfolio_data(self, collector):
        result = collector.collect_portfolio_data()

        assert "total_market_value" in result
        assert "total_profit_loss" in result
        assert "timestamp" in result

    def test_collect_stock_info(self, collector):
        results = collector.collect_stock_info(["005930"])

        assert len(results) == 1
        assert results[0]["stockNo"] == "005930"
        assert results[0]["stockNm"] == "Samsung"

    def test_collect_stock_info_empty(self, mock_kis_api, mock_order_manager, mock_portfolio):
        mock_kis_api.get_stock_info.return_value = None
        collector = InformationCollector(mock_kis_api, mock_order_manager, mock_portfolio)
        results = collector.collect_stock_info(["005930"])

        assert len(results) == 0

    def test_collect_market_trend(self, collector):
        result = collector.collect_market_trend("005930", count=10)

        assert "items" in result
        assert len(result["items"]) == 2

    def test_collect_all_data(self, collector):
        result = collector.collect_all_data(["005930"])

        assert "market_data" in result
        assert "portfolio_summary" in result
        assert "stock_infos" in result
        assert "collected_at" in result

    def test_collect_all_data_default_stock(self, collector):
        result = collector.collect_all_data()

        assert len(result["market_data"]) == 1

    def test_get_collected_data(self, collector):
        collector.collect_market_data(["005930"])
        data = collector.get_collected_data("005930")

        assert len(data) == 1
        assert data[0].stock_code == "005930"

    def test_get_collected_data_all(self, collector):
        collector.collect_market_data(["005930"])
        data = collector.get_collected_data()

        assert len(data) == 1

    def test_clear_collected_data(self, collector):
        collector.collect_market_data(["005930"])
        collector.clear_collected_data()

        assert len(collector.get_collected_data()) == 0

    def test_analyze_market_sentiment_bullish(self, collector):
        sentiment = collector.analyze_market_sentiment("005930")
        assert sentiment == "BULLISH"

    def test_analyze_market_sentiment_bearish(self, mock_kis_api, mock_order_manager, mock_portfolio):
        mock_kis_api.get_market_data.return_value = {
            "price": 70000.0,
            "changeRate": -5.0,
            "volume": 1000000,
        }
        collector = InformationCollector(mock_kis_api, mock_order_manager, mock_portfolio)
        sentiment = collector.analyze_market_sentiment("005930")
        assert sentiment == "BEARISH"

    def test_analyze_market_sentiment_neutral(self, mock_kis_api, mock_order_manager, mock_portfolio):
        mock_kis_api.get_market_data.return_value = {
            "price": 70000.0,
            "changeRate": 2.0,
            "volume": 1000000,
        }
        collector = InformationCollector(mock_kis_api, mock_order_manager, mock_portfolio)
        sentiment = collector.analyze_market_sentiment("005930")
        assert sentiment == "NEUTRAL"

    def test_generate_trading_signal_buy(self, collector):
        signal = collector.generate_trading_signal("005930", "BULLISH")
        assert signal["signal"] == "BUY"
        assert signal["stock_code"] == "005930"

    def test_generate_trading_signal_sell(self, collector):
        signal = collector.generate_trading_signal("005930", "BEARISH")
        assert signal["signal"] == "SELL"
        assert signal["stock_code"] == "005930"

    def test_generate_trading_signal_none(self, collector):
        signal = collector.generate_trading_signal("005930", "NEUTRAL")
        assert signal is None