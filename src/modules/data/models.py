from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import declarative_base, relationship
import enum

Base = declarative_base()


class TradeSide(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class TradeStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class StockInfo(Base):
    __tablename__ = "stock_info"

    stock_code = Column(String(6), primary_key=True)
    stock_name = Column(String(100), nullable=False)
    market_type = Column(String(20), nullable=False)
    sector = Column(String(100))

    market_data = relationship("MarketData", back_populates="stock_info")

    def __repr__(self):
        return f"<StockInfo(code={self.stock_code}, name={self.stock_name})>"


class MarketData(Base):
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_code = Column(
        String(6), ForeignKey("stock_info.stock_code"), nullable=False
    )
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    current_price = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    change_rate = Column(Float)

    stock_info = relationship("StockInfo", back_populates="market_data")

    def __repr__(self):
        return f"<MarketData(stock_code={self.stock_code}, price={self.current_price})>"


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_code = Column(String(6), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    side = Column(Enum(TradeSide), nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(Enum(TradeStatus), default=TradeStatus.PENDING)

    def __repr__(self):
        return f"<Trade(id={self.id}, stock={self.stock_code}, side={self.side.value})>"


class Performance(Base):
    __tablename__ = "performance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    total_pnl = Column(Float, default=0.0)
    win_rate = Column(Float, default=0.0)
    profit_factor = Column(Float, default=0.0)

    def __repr__(self):
        return f"<Performance(pnl={self.total_pnl}, win_rate={self.win_rate})>"
