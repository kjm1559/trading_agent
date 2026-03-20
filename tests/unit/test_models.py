import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.modules.data.models import (
    Base,
    StockInfo,
    MarketData,
    Trade,
    Performance,
    TradeSide,
    TradeStatus,
)


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


class TestTradeSideEnum:
    def test_buy_value(self):
        assert TradeSide.BUY.value == "BUY"

    def test_sell_value(self):
        assert TradeSide.SELL.value == "SELL"

    def test_all_values(self):
        assert set(s.value for s in TradeSide) == {"BUY", "SELL"}


class TestTradeStatusEnum:
    def test_pending_value(self):
        assert TradeStatus.PENDING.value == "PENDING"

    def test_completed_value(self):
        assert TradeStatus.COMPLETED.value == "COMPLETED"

    def test_cancelled_value(self):
        assert TradeStatus.CANCELLED.value == "CANCELLED"


class TestStockInfo:
    def test_create_stock_info(self, in_memory_db):
        stock = StockInfo(
            stock_code="005930",
            stock_name="삼성전자",
            market_type="KOSPI",
            sector="전자",
        )
        in_memory_db.add(stock)
        in_memory_db.commit()

        assert stock.stock_code == "005930"
        assert stock.stock_name == "삼성전자"

    def test_stock_info_repr(self):
        stock = StockInfo(stock_code="005930", stock_name="삼성전자")
        assert "005930" in repr(stock)
        assert "삼성전자" in repr(stock)

    def test_stock_info_unique_code(self, in_memory_db):
        stock1 = StockInfo(
            stock_code="005930", stock_name="삼성전자", market_type="KOSPI"
        )
        stock2 = StockInfo(
            stock_code="005930", stock_name="다른 이름", market_type="KOSPI"
        )

        in_memory_db.add(stock1)
        in_memory_db.commit()

        in_memory_db.add(stock2)

        from sqlalchemy.exc import IntegrityError
        with pytest.raises(IntegrityError):
            in_memory_db.commit()


class TestMarketData:
    def test_create_market_data(self, in_memory_db):
        stock = StockInfo(
            stock_code="005930", stock_name="삼성전자", market_type="KOSPI"
        )
        in_memory_db.add(stock)
        in_memory_db.commit()

        market_data = MarketData(
            stock_code="005930", current_price=70000.0, volume=1000000,
            change_rate=2.5,
        )
        in_memory_db.add(market_data)
        in_memory_db.commit()

        assert market_data.current_price == 70000.0
        assert market_data.volume == 1000000

    def test_market_data_relationship(self, in_memory_db):
        stock = StockInfo(
            stock_code="005930", stock_name="삼성전자", market_type="KOSPI"
        )
        market_data = MarketData(
            stock_code="005930", current_price=70000.0, volume=1000000
        )

        in_memory_db.add(stock)
        in_memory_db.add(market_data)
        in_memory_db.commit()

        assert market_data.stock_info.stock_code == "005930"
        assert stock.market_data[0].current_price == 70000.0

    def test_market_data_timestamp_default(self, in_memory_db):
        stock = StockInfo(
            stock_code="005930", stock_name="삼성전자", market_type="KOSPI"
        )
        market_data = MarketData(
            stock_code="005930", current_price=70000.0, volume=1000000
        )

        in_memory_db.add(stock)
        in_memory_db.add(market_data)
        in_memory_db.commit()

        assert market_data.timestamp is not None


class TestTrade:
    def test_create_trade_buy(self, in_memory_db):
        trade = Trade(
            stock_code="005930",
            side=TradeSide.BUY,
            price=70000.0,
            quantity=100,
        )
        in_memory_db.add(trade)
        in_memory_db.commit()

        assert trade.side == TradeSide.BUY
        assert trade.status == TradeStatus.PENDING

    def test_create_trade_sell(self, in_memory_db):
        trade = Trade(
            stock_code="005930",
            side=TradeSide.SELL,
            price=70000.0,
            quantity=100,
        )
        in_memory_db.add(trade)
        in_memory_db.commit()

        assert trade.side == TradeSide.SELL

    def test_trade_repr(self):
        trade = Trade(stock_code="005930", side=TradeSide.BUY)
        assert "005930" in repr(trade)
        assert "BUY" in repr(trade)


class TestPerformance:
    def test_create_performance(self, in_memory_db):
        perf = Performance(total_pnl=100000.0, win_rate=0.6, profit_factor=1.5)
        in_memory_db.add(perf)
        in_memory_db.commit()

        assert perf.total_pnl == 100000.0
        assert perf.win_rate == 0.6
        assert perf.profit_factor == 1.5

    def test_performance_defaults(self, in_memory_db):
        perf = Performance()
        in_memory_db.add(perf)
        in_memory_db.commit()

        assert perf.total_pnl == 0.0
        assert perf.win_rate == 0.0
        assert perf.profit_factor == 0.0

    def test_performance_timestamp(self, in_memory_db):
        perf = Performance()
        in_memory_db.add(perf)
        in_memory_db.commit()

        assert perf.timestamp is not None
