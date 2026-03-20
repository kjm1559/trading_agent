import logging
import pytest
import tempfile
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler

from src.modules.shared.utils import (
    setup_logging,
    get_logger,
    TradingError,
    KISAPIError,
    ValidationError,
    OrderExecutionError,
)


class TestSetupLogging:
    def test_setup_logging_returns_logger(self):
        logger = setup_logging()
        assert isinstance(logger, logging.Logger)

    def test_setup_logging_default_level(self):
        logger = setup_logging()
        assert logger.level == logging.INFO

    def test_setup_logging_debug_level(self):
        logger = setup_logging(log_level="DEBUG")
        assert logger.level == logging.DEBUG

    def test_setup_logging_error_level(self):
        logger = setup_logging(log_level="ERROR")
        assert logger.level == logging.ERROR

    def test_setup_logging_console_handler(self):
        logger = setup_logging()
        console_handlers = [
            h for h in logger.handlers if isinstance(h, logging.StreamHandler)
        ]
        assert len(console_handlers) > 0

    def test_setup_logging_creates_log_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "subdir", "test.log")
            logger = setup_logging(log_file=log_file)
            assert Path(log_file).parent.exists()

    def test_setup_logging_file_handler(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            logger = setup_logging(log_file=log_file)
            file_handlers = [
                h for h in logger.handlers if isinstance(h, RotatingFileHandler)
            ]
            assert len(file_handlers) > 0

    def test_setup_logging_no_duplicate_handlers(self):
        logger = setup_logging()
        handlers_before = len(logger.handlers)
        logger = setup_logging()
        handlers_after = len(logger.handlers)
        assert handlers_before == handlers_after


class TestGetLogger:
    def test_get_logger_returns_logger(self):
        logger = get_logger("test_module")
        assert isinstance(logger, logging.Logger)

    def test_get_logger_name(self):
        logger = get_logger("test_module")
        assert logger.name == "trading_agent.test_module"


class TestErrorHierarchy:
    def test_trading_error_is_exception(self):
        try:
            raise TradingError("test error")
        except Exception as e:
            assert str(e) == "test error"

    def test_kisapi_error_inherits_trading_error(self):
        try:
            raise KISAPIError("api error")
        except TradingError:
            pass

    def test_validation_error_inherits_trading_error(self):
        try:
            raise ValidationError("validation failed")
        except TradingError:
            pass

    def test_order_execution_error_inherits_trading_error(self):
        try:
            raise OrderExecutionError("order failed")
        except TradingError:
            pass
