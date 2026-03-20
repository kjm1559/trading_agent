import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()


class Config:
    @classmethod
    def _get_str(cls, key: str, default: Optional[str] = None) -> Optional[str]:
        return os.getenv(key, default) or default

    @classmethod
    def _get_int(cls, key: str, default: int) -> int:
        try:
            return int(os.getenv(key, str(default)))
        except (ValueError, TypeError):
            return default

    @classmethod
    def _get_float(cls, key: str, default: float) -> float:
        try:
            return float(os.getenv(key, str(default)))
        except (ValueError, TypeError):
            return default

    @property
    def openai_base_url(self) -> str:
        return Config._get_str("OPENAI_BASE_URL", "https://api.openai.com/v1") or "https://api.openai.com/v1"

    @property
    def openai_api_key(self) -> Optional[str]:
        return Config._get_str("OPENAI_API_KEY")

    @property
    def openai_model(self) -> str:
        return Config._get_str("OPENAI_MODEL", "gpt-4o") or "gpt-4o"

    @property
    def kis_app_key(self) -> Optional[str]:
        return Config._get_str("KIS_APP_KEY")

    @property
    def kis_app_secret(self) -> Optional[str]:
        return Config._get_str("KIS_APP_SECRET")

    @property
    def kis_account_type(self) -> str:
        return Config._get_str("KIS_ACCOUNT_TYPE", "VIRTUAL") or "VIRTUAL"

    @property
    def kis_cano(self) -> Optional[str]:
        return Config._get_str("KIS_CANO")

    @property
    def kis_base_url(self) -> str:
        return Config._get_str("KIS_BASE_URL", "https://apis.openapi.koreainvestment.com") or "https://apis.openapi.koreainvestment.com"

    @property
    def kis_access_token(self) -> str:
        return Config._get_str("KIS_ACCESS_TOKEN", "") or ""

    @property
    def agent_interval_hours(self) -> int:
        return Config._get_int("AGENT_INTERVAL_HOURS", 24)

    @property
    def aggressiveness(self) -> float:
        return Config._get_float("AGGRESSIVENESS", 0.5)

    @property
    def risk_tolerance(self) -> float:
        return Config._get_float("RISK_TOLERANCE", 0.1)

    @property
    def db_path(self) -> str:
        return Config._get_str("DB_PATH", "./data/trading.db") or "./data/trading.db"

    @property
    def log_level(self) -> str:
        return Config._get_str("LOG_LEVEL", "INFO") or "INFO"

    @property
    def log_file(self) -> str:
        return Config._get_str("LOG_FILE", "./logs/trading.log") or "./logs/trading.log"


def validate_config():
    config = Config()
    errors = []
    if not config.openai_api_key:
        errors.append("OPENAI_API_KEY not set")
    if not config.kis_app_key:
        errors.append("KIS_APP_KEY not set")
    if not config.kis_app_secret:
        errors.append("KIS_APP_SECRET not set")
    if not config.kis_cano:
        errors.append("KIS_CANO not set")
    if errors:
        raise ValueError("Configuration error: " + ", ".join(errors))


def get_config() -> Config:
    return Config()
