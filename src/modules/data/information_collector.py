import asyncio
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from src.modules.trading.kis_api import KISAPI
from src.modules.trading.order_manager import OrderManager
from src.modules.trading.portfolio import Portfolio
from src.modules.data.models import StockInfo, MarketData
from src.modules.data.db import get_session


@dataclass
class CollectedData:
    timestamp: datetime
    stock_code: str
    market_data: Dict[str, Any]
    portfolio_summary: Optional[Dict[str, Any]] = None
    analysis_result: Optional[Dict[str, Any]] = None


class InformationCollector:
    def __init__(
        self,
        kis_api: Optional[KISAPI] = None,
        order_manager: Optional[OrderManager] = None,
        portfolio: Optional[Portfolio] = None,
    ):
        self.kis_api = kis_api or KISAPI()
        self.order_manager = order_manager or OrderManager(kis_api)
        self.portfolio = portfolio or Portfolio(kis_api, self.order_manager)
        self.collected_data: List[CollectedData] = []

    def collect_market_data(self, stock_codes: List[str]) -> List[CollectedData]:
        results = []
        for stock_code in stock_codes:
            market_data = self.kis_api.get_market_data(stock_code)
            if market_data:
                collected = CollectedData(
                    timestamp=datetime.now(),
                    stock_code=stock_code,
                    market_data=market_data,
                )
                results.append(collected)
                self.collected_data.append(collected)
        return results

    def collect_portfolio_data(self) -> Dict[str, Any]:
        summary = self.portfolio.get_portfolio_summary()
        return {
            "total_market_value": summary.total_market_value,
            "total_cost_value": summary.total_cost_value,
            "total_profit_loss": summary.total_profit_loss,
            "total_profit_rate": summary.total_profit_rate,
            "cash": summary.cash,
            "total_assets": summary.total_assets,
            "holdings": summary.holdings,
            "timestamp": datetime.now().isoformat(),
        }

    def collect_stock_info(self, stock_codes: List[str]) -> List[Dict]:
        results = []
        for stock_code in stock_codes:
            stock_info = self.kis_api.get_stock_info(stock_code)
            if stock_info:
                results.append(stock_info)
        return results

    def collect_market_trend(
        self, stock_code: str, count: int = 10, timeframe: str = "m1"
    ) -> Dict:
        return self.kis_api.get_market_trend(stock_code, count, timeframe)

    def collect_all_data(
        self, stock_codes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        stock_codes = stock_codes or ["005930"]
        
        market_data = self.collect_market_data(stock_codes)
        portfolio_summary = self.collect_portfolio_data()
        stock_infos = self.collect_stock_info(stock_codes)

        return {
            "market_data": [vars(d) for d in market_data],
            "portfolio_summary": portfolio_summary,
            "stock_infos": stock_infos,
            "collected_at": datetime.now().isoformat(),
        }

    def save_collected_data(self, data: Dict[str, Any]) -> None:
        with get_session() as session:
            for item in data.get("market_data", []):
                market_record = MarketData(
                    stock_code=item["stock_code"],
                    price=item["market_data"].get("price", 0),
                    change_price=item["market_data"].get("changePrice", 0),
                    volume=item["market_data"].get("volume", 0),
                    timestamp=item["timestamp"],
                )
                session.add(market_record)

    def get_collected_data(self, stock_code: Optional[str] = None) -> List[CollectedData]:
        if stock_code:
            return [d for d in self.collected_data if d.stock_code == stock_code]
        return self.collected_data

    def clear_collected_data(self) -> None:
        self.collected_data.clear()

    async def collect_periodically(
        self,
        stock_codes: List[str],
        interval_seconds: int = 60,
    ):
        while True:
            asyncio.create_task(self.collect_market_data(stock_codes))
            await asyncio.sleep(interval_seconds)

    def analyze_market_sentiment(self, stock_code: str) -> str:
        market_data = self.kis_api.get_market_data(stock_code)
        if not market_data:
            return "NEUTRAL"

        change_rate = float(market_data.get("changeRate", 0))
        volume = float(market_data.get("volume", 0))

        if change_rate > 5 and volume > 0:
            return "BULLISH"
        elif change_rate < -5 and volume > 0:
            return "BEARISH"
        else:
            return "NEUTRAL"

    def generate_trading_signal(
        self, stock_code: str, sentiment: str
    ) -> Optional[Dict]:
        if sentiment == "BULLISH":
            return {
                "stock_code": stock_code,
                "signal": "BUY",
                "reason": f"{sentiment} market sentiment detected",
            }
        elif sentiment == "BEARISH":
            return {
                "stock_code": stock_code,
                "signal": "SELL",
                "reason": f"{sentiment} market sentiment detected",
            }
        else:
            return None