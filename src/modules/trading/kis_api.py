import httpx
from typing import Optional
from src.modules.shared.config import Config


class KISAPI:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.base_url = self.config.kis_base_url
        self.access_token = self.config.kis_access_token

    def get_headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "authorization": f"Bearer {self.access_token}",
        }

    def request(self, method: str, endpoint: str, params: Optional[dict] = None) -> dict:
        headers = self.get_headers()
        url = f"{self.base_url}{endpoint}"

        response = httpx.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
        )
        response.raise_for_status()
        return response.json()

    def get_market_trend(self, stock_code: str, count: int) -> dict:
        endpoint = "/openapi/v2/marketTrend/list"
        params = {"marketCode": "EQ", "cnt": count, "sortOrd": "D"}
        return self.request("GET", endpoint, params)

    def get_stocks_list(self, market_code: str) -> dict:
        endpoint = "/openapi/v2/marketTrend/list"
        params = {"marketCode": market_code, "cnt": 1000, "sortOrd": "A"}
        return self.request("GET", endpoint, params)

    def get_stock_info(self, stock_code: str) -> Optional[dict]:
        stocks_list = self.get_stocks_list("EQ")
        items = stocks_list.get("items", [])
        for item in items:
            if item.get("stockNo") == stock_code:
                return item
        return None

    def get_market_data(self, stock_code: str) -> dict:
        endpoint = f"/openapi/v2/marketTrend/realtime"
        params = {"marketTimeValueCode": stock_code}
        return self.request("GET", endpoint, params)

    def get_account_balance(self) -> dict:
        endpoint = "/openapi/v2/approval/balance"
        return self.request("GET", endpoint)

    def get_positions(self) -> dict:
        endpoint = "/openapi/v2/approval/asset"
        return self.request("GET", endpoint)

    def get_orders(self, start_time: str, end_time: str) -> dict:
        endpoint = "/openapi/v2/approval/trade/list"
        params = {"startTime": start_time, "endTime": end_time}
        return self.request("GET", endpoint, params)

    def submit_order(
        self,
        stock_code: str,
        quantity: int,
        price: float,
        order_type: str = "BUY",
    ) -> dict:
        endpoint = "/openapi/v2/approval/trade/submit"
        data = {
            "inPrice": str(price),
            "inQty": str(quantity),
            "orderCode": "12",
            "stockNo": stock_code,
            "hoidcode": order_type,
        }
        return self.request("POST", endpoint, data)

    def cancel_order(self, order_key: str) -> dict:
        endpoint = "/openapi/v2/approval/trade/cancel"
        data = {"orders": [order_key]}
        return self.request("POST", endpoint, data)
