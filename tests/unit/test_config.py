import os
import pytest
from unittest.mock import patch

from src.modules.shared.config import Config, validate_config, get_config


class TestConfigDefaultValues:
    def test_openai_base_url_default(self):
        config = Config()
        assert config.openai_base_url == "https://api.openai.com/v1"

    def test_openai_model_default(self):
        config = Config()
        assert config.openai_model == "gpt-4o"

    def test_kis_account_type_default(self):
        config = Config()
        assert config.kis_account_type == "VIRTUAL"

    def test_agent_interval_hours_default(self):
        config = Config()
        assert config.agent_interval_hours == 24

    def test_aggressiveness_default(self):
        config = Config()
        assert config.aggressiveness == 0.5

    def test_risk_tolerance_default(self):
        config = Config()
        assert config.risk_tolerance == 0.1

    def test_db_path_default(self):
        config = Config()
        assert config.db_path == "./data/trading.db"


class TestConfigEnvValues:
    @patch.dict(os.environ, {
        "OPENAI_BASE_URL": "https://custom.url/v1",
        "OPENAI_MODEL": "gpt-3.5-turbo",
    })
    def test_custom_openai_config(self):
        config = Config()
        assert config.openai_base_url == "https://custom.url/v1"
        assert config.openai_model == "gpt-3.5-turbo"

    @patch.dict(os.environ, {
        "AGENT_INTERVAL_HOURS": "12",
        "AGGRESSIVENESS": "0.8",
    })
    def test_custom_agent_config(self):
        config = Config()
        assert config.agent_interval_hours == 12
        assert config.aggressiveness == 0.8


class TestConfigValidation:
    @patch.dict(os.environ, {}, clear=True)
    def test_validate_missing_openai_key(self):
        with pytest.raises(ValueError) as excinfo:
            validate_config()
        assert "OPENAI_API_KEY not set" in str(excinfo.value)

    @patch.dict(os.environ, {
        "OPENAI_API_KEY": "test-key",
    }, clear=True)
    def test_validate_missing_kis_keys(self):
        with pytest.raises(ValueError) as excinfo:
            validate_config()
        assert "KIS_APP_KEY not set" in str(excinfo.value)
        assert "KIS_APP_SECRET not set" in str(excinfo.value)

    @patch.dict(os.environ, {
        "OPENAI_API_KEY": "test-key",
        "KIS_APP_KEY": "test-app-key",
        "KIS_APP_SECRET": "test-secret",
    }, clear=True)
    def test_validate_missing_cano(self):
        with pytest.raises(ValueError) as excinfo:
            validate_config()
        assert "KIS_CANO not set" in str(excinfo.value)

    @patch.dict(os.environ, {
        "OPENAI_API_KEY": "test-key",
        "KIS_APP_KEY": "test-app-key",
        "KIS_APP_SECRET": "test-secret",
        "KIS_CANO": "test-cano",
    }, clear=True)
    def test_validate_all_keys_set(self):
        validate_config()


class TestGetConfig:
    def test_get_config_returns_config_instance(self):
        config = get_config()
        assert isinstance(config, Config)
