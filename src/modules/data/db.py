from typing import Generator
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

from src.modules.shared.config import Config
from src.modules.data.models import Base


def get_db_engine() -> Engine:
    config = Config()
    engine = create_engine(f"sqlite:///{config.db_path}", future=True)
    Base.metadata.create_all(bind=engine)
    return engine


SessionLocal = sessionmaker()


@contextmanager
def get_session() -> Generator[Session, None, None]:
    engine = get_db_engine()
    SessionLocal.configure(bind=engine)
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()