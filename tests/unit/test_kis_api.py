import pytest
import httpx
from unittest.mock import Mock, patch, MagicMock

from src.modules.trading.kis_api import KISAPI


class TestKISAPI:
    @pytest.fixture
    def mock_config(self):
        config = MagicMock()
        config.kis_base_url = "https://test.kis.com"
        config.kis_access_token = "test_token"
        return config

    def test_init_with_config(self, mock_config):
        api = KISAPI(mock_config)
        assert api.base_url == "https://test.kis.com"
        assert api.access_token == "test_token"

    def test_get_headers(self, mock_config):
        api = KISAPI(mock_config)
        headers = api.get_headers()

        assert headers["Content-Type"] == "application/json"
        assert headers["authorization"] == "Bearer test_token"

    @patch("httpx.request")
    def test_request_success(self, mock_request, mock_config):
        mock_response = Mock()
        mock_response.json.return_value = {"data": "test"}
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        api = KISAPI(mock_config)
        result = api.request("GET", "/test", {"param": "value"})

        assert result == {"data": "test"}
        mock_request.assert_called_once()

    @patch("httpx.request")
    def test_request_raises_on_error(self, mock_request, mock_config):
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Error",
            request=Mock(),
            response=Mock(),
        )
        mock_request.return_value = mock_response

        api = KISAPI(mock_config)

        with pytest.raises(httpx.HTTPStatusError):
            api.request("GET", "/test")

    @patch.object(KISAPI, "request")
    def test_get_market_trend(self, mock_request, mock_config):
        mock_request.return_value = {"items": [{"stockNo": "005930"}]}

        api = KISAPI(mock_config)
        result = api.get_market_trend("005930", 10)

        assert "items" in result
        mock_request.assert_called()

    @patch.object(KISAPI, "request")
    def test_get_stocks_list(self, mock_request, mock_config):
        mock_request.return_value = {"items": [{"stockNo": "005930"}]}

        api = KISAPI(mock_config)
        result = api.get_stocks_list("EQ")

        assert "items" in result
        mock_request.assert_called()

    @patch.object(KISAPI, "get_stocks_list")
    def test_get_stock_info_found(self, mock_get_stocks_list, mock_config):
        mock_get_stocks_list.return_value = {
            "items": [{"stockNo": "005930", "stockNm": "Samsung"}]
        }

        api = KISAPI(mock_config)
        result = api.get_stock_info("005930")

        assert result is not None
        assert result["stockNo"] == "005930"

    @patch.object(KISAPI, "get_stocks_list")
    def test_get_stock_info_not_found(self, mock_get_stocks_list, mock_config):
        mock_get_stocks_list.return_value = {"items": [{"stockNo": "123456"}]}

        api = KISAPI(mock_config)
        result = api.get_stock_info("005930")

        assert result is None

    @patch.object(KISAPI, "request")
    def test_get_market_data(self, mock_request, mock_config):
        mock_request.return_value = {"data": "market_data"}

        api = KISAPI(mock_config)
        result = api.get_market_data("005930")

        assert "data" in result
        mock_request.assert_called()

    @patch.object(KISAPI, "request")
    def test_get_account_balance(self, mock_request, mock_config):
        mock_request.return_value = {"balance": 1000000}

        api = KISAPI(mock_config)
        result = api.get_account_balance()

        assert "balance" in result
        mock_request.assert_called()

    @patch.object(KISAPI, "request")
    def test_get_positions(self, mock_request, mock_config):
        mock_request.return_value = {"positions": [{"stockNo": "005930"}]}

        api = KISAPI(mock_config)
        result = api.get_positions()

        assert "positions" in result
        mock_request.assert_called()

    @patch.object(KISAPI, "request")
    def test_get_orders(self, mock_request, mock_config):
        mock_request.return_value = {"orders": [{"orderKey": "123"}]}

        api = KISAPI(mock_config)
        result = api.get_orders("20250101", "20251231")

        assert "orders" in result
        mock_request.assert_called()

    @patch.object(KISAPI, "request")
    def test_submit_order(self, mock_request, mock_config):
        mock_request.return_value = {"orderKey": "456"}

        api = KISAPI(mock_config)
        result = api.submit_order("005930", 100, 70000)

        assert "orderKey" in result
        mock_request.assert_called()

    @patch.object(KISAPI, "request")
    def test_cancel_order(self, mock_request, mock_config):
        mock_request.return_value = {"status": "success"}

        api = KISAPI(mock_config)
        result = api.cancel_order("123456")

        assert "status" in result
        mock_request.assert_called()