import pytest
import tempfile
import os
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.modules.data.db import get_db_engine, get_session, SessionLocal
from src.modules.data.models import StockInfo, Trade, TradeSide


class TestGetDbEngine:
    def test_get_db_engine_returns_engine(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            os.environ["DB_PATH"] = db_path

            from src.modules.data import db
            from importlib import reload
            reload(db)

            engine = db.get_db_engine()
            assert engine is not None

    def test_get_db_engine_creates_tables(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            os.environ["DB_PATH"] = db_path

            from src.modules.data import db
            from importlib import reload
            reload(db)

            engine = db.get_db_engine()
            conn = engine.connect()
            inspect_result = conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table';")
            )
            tables = {row[0] for row in inspect_result}

            assert "stock_info" in tables
            assert "trades" in tables


class TestGetSession:
    def test_get_session_returns_context_manager(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            os.environ["DB_PATH"] = db_path

            from src.modules.data import db
            from importlib import reload
            reload(db)

            context_manager = db.get_session()
            assert hasattr(context_manager, "__enter__")
            assert hasattr(context_manager, "__exit__")

    def test_get_session_provides_session(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            os.environ["DB_PATH"] = db_path

            from src.modules.data import db
            from importlib import reload
            reload(db)

            with db.get_session() as session:
                assert isinstance(session, Session)

    def test_get_session_auto_commits(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            os.environ["DB_PATH"] = db_path

            from src.modules.data import db
            from importlib import reload
            reload(db)

            with db.get_session() as session:
                stock = StockInfo(
                    stock_code="005930",
                    stock_name="Samsung",
                    market_type="KOSPI",
                )
                session.add(stock)

            with db.get_session() as session:
                stock = session.query(StockInfo).filter_by(stock_code="005930").first()
                assert stock is not None

    def test_get_session_rollback_on_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            os.environ["DB_PATH"] = db_path

            from src.modules.data import db
            from importlib import reload
            reload(db)

            try:
                with db.get_session() as session:
                    stock = StockInfo(
                        stock_code="005930",
                        stock_name="Samsung",
                        market_type="KOSPI",
                    )
                    session.add(stock)
                    raise ValueError("Test error")
            except ValueError:
                pass

            with db.get_session() as session:
                stock = session.query(StockInfo).filter_by(stock_code="005930").first()
                assert stock is None