import pytest
from unittest.mock import Mock, patch, AsyncMock

from src.modules.shared.config import Config
from src.modules.telegram_bot.bot import TelegramBot


class TestTelegramBot:
    @pytest.fixture
    def mock_config(self):
        """Create a mock config for testing."""
        config = Mock(spec=Config)
        config.telegram_bot_token = "test_bot_token_123"
        config.telegram_authorized_users = ["123456789", "987654321"]
        return config

    def test_bot_initialization(self, mock_config):
        """Test TelegramBot initializes with valid config."""
        bot = TelegramBot(mock_config)
        assert bot.token == "test_bot_token_123"
        assert bot.authorized_users == ["123456789", "987654321"]
        assert not bot.is_running()
        assert not bot.is_paused()

    def test_bot_initialization_no_token(self):
        """Test TelegramBot handles missing token gracefully."""
        config = Mock(spec=Config)
        config.telegram_bot_token = None
        config.telegram_authorized_users = []

        bot = TelegramBot(config)
        assert bot.bot is None
        assert bot.dispatcher is None

    def test_is_authorized_valid_user(self, mock_config):
        """Test authorization check for valid user."""
        bot = TelegramBot(mock_config)
        assert bot.is_authorized("123456789") is True
        assert bot.is_authorized("987654321") is True

    def test_is_authorized_invalid_user(self, mock_config):
        """Test authorization check for invalid user."""
        bot = TelegramBot(mock_config)
        assert bot.is_authorized("555555555") is False

    def test_running_state(self, mock_config):
        """Test running state management."""
        bot = TelegramBot(mock_config)
        assert bot.is_running() is False

        bot.set_running(True)
        assert bot.is_running() is True

        bot.set_running(False)
        assert bot.is_running() is False

    def test_paused_state(self, mock_config):
        """Test paused state management."""
        bot = TelegramBot(mock_config)
        assert bot.is_paused() is False

        bot.set_paused(True)
        assert bot.is_paused() is True

        bot.set_paused(False)
        assert bot.is_paused() is False

    @pytest.mark.asyncio
    async def test_send_message_without_bot(self):
        """Test sending message when bot is not initialized."""
        config = Mock(spec=Config)
        config.telegram_bot_token = None
        config.telegram_authorized_users = []

        bot = TelegramBot(config)
        result = await bot.send_message("123456789", "test message")
        assert result is False

    @pytest.mark.asyncio
    async def test_send_message_success(self, mock_config):
        """Test sending message successfully (mocked)."""
        with patch('src.modules.telegram_bot.bot.Bot') as MockBot:
            mock_bot_instance = AsyncMock()
            MockBot.return_value = mock_bot_instance

            bot = TelegramBot(mock_config)
            bot.bot = mock_bot_instance

            result = await bot.send_message("123456789", "Test message")
            assert result is True
            mock_bot_instance.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_message_failure(self, mock_config):
        """Test sending message fails (mocked exception)."""
        with patch('src.modules.telegram_bot.bot.Bot') as MockBot:
            mock_bot_instance = AsyncMock()
            mock_bot_instance.send_message.side_effect = Exception("Network error")
            MockBot.return_value = mock_bot_instance

            bot = TelegramBot(mock_config)
            bot.bot = mock_bot_instance

            result = await bot.send_message("123456789", "Test message")
            assert result is False

    def test_orchestrator_reference(self, mock_config):
        """Test setting orchestrator reference."""
        bot = TelegramBot(mock_config)
        assert bot.orchestrator is None

        mock_orchestrator = Mock()
        bot.set_orchestrator(mock_orchestrator)
        assert bot.orchestrator is mock_orchestrator

    @pytest.mark.asyncio
    async def test_trigger_agent_analysis_with_orchestrator(self, mock_config):
        """Test triggering agent analysis with orchestrator."""
        bot = TelegramBot(mock_config)
        mock_orchestrator = Mock()
        mock_orchestrator.trigger_agent_analysis = AsyncMock()
        bot.set_orchestrator(mock_orchestrator)

        await bot.trigger_agent_analysis("123456789")
        mock_orchestrator.trigger_agent_analysis.assert_called_once_with("123456789")

    @pytest.mark.asyncio
    async def test_trigger_agent_analysis_without_orchestrator(self, mock_config):
        """Test triggering agent analysis without orchestrator."""
        with patch('src.modules.telegram_bot.bot.Bot') as MockBot:
            mock_bot_instance = AsyncMock()
            MockBot.return_value = mock_bot_instance

            bot = TelegramBot(mock_config)
            bot.bot = mock_bot_instance

            await bot.trigger_agent_analysis("123456789")
            mock_bot_instance.send_message.assert_called_once()

    def test_load_authorized_users_empty(self):
        """Test loading empty authorized users."""
        config = Mock(spec=Config)
        config.telegram_bot_token = "test_token"
        config.telegram_authorized_users = []

        bot = TelegramBot(config)
        assert len(bot.authorized_users) == 0