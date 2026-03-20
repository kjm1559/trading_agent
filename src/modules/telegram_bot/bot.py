"""Telegram Bot implementation using aiogram 3.x for Trading Agent notifications."""

import logging
from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.types import Message

from src.modules.shared.config import Config

logger = logging.getLogger(__name__)


class TelegramBot:
    """Async Telegram bot for sending notifications and receiving commands.
    
    Supports:
    - User authentication check based on authorized user IDs
    - Bot state management (running/paused)
    - Async messaging with aiogram 3.x
    """
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the Telegram bot.
        
        Args:
            config: Configuration instance. If None, uses default Config().
        
        Raises:
            ValueError: If telegram_bot_token is not configured.
        """
        self.config = config or Config()
        self.token = self.config.telegram_bot_token
        
        if not self.token:
            logger.warning("Telegram bot token not configured")
            self.bot: Optional[Bot] = None
            self.dispatcher: Optional[Dispatcher] = None
        else:
            try:
                self.bot = Bot(token=self.token)
                self.dispatcher = Dispatcher()
                logger.info("Telegram bot initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Telegram bot: {e}")
                self.bot = None
                self.dispatcher = None
        
        # Bot state management
        self._running: bool = False
        self._paused: bool = False
        
        # Get authorized users from config
        self.authorized_users = self._load_authorized_users()
        logger.info(f"Loaded {len(self.authorized_users)} authorized users")

        # Reference to orchestrator (optional)
        self.orchestrator = None

    def set_orchestrator(self, orchestrator) -> None:
        """Set the orchestrator reference for triggering actions."""
        self.orchestrator = orchestrator
        logger.info("Orchestrator reference set")
    
    def _load_authorized_users(self) -> list[str]:
        """Load authorized user IDs from configuration."""
        users = self.config.telegram_authorized_users
        logger.debug(f"Authorized users from config: {users}")
        return users
    
    def is_authorized(self, user_id: str) -> bool:
        """Check if a user is authorized to use the bot.
        
        Args:
            user_id: Telegram user ID to check.
            
        Returns:
            True if user is authorized, False otherwise.
        """
        is_auth = user_id in self.authorized_users
        if not is_auth:
            logger.warning(f"Unauthorized access attempt from user: {user_id}")
        return is_auth
    
    def is_running(self) -> bool:
        """Check if the bot is currently running.
        
        Returns:
            True if bot is running, False otherwise.
        """
        return self._running
    
    def set_running(self, running: bool) -> None:
        """Set the bot running state.
        
        Args:
            running: True to start bot, False to stop.
        """
        self._running = running
        status = "started" if running else "stopped"
        logger.info(f"Telegram bot {status}")
    
    def is_paused(self) -> bool:
        """Check if the bot is currently paused.
        
        Returns:
            True if bot is paused, False otherwise.
        """
        return self._paused
    
    def set_paused(self, paused: bool) -> None:
        """Set the bot paused state.
        
        Args:
            paused: True to pause bot, False to resume.
        """
        self._paused = paused
        status = "paused" if paused else "resumed"
        logger.info(f"Telegram bot {status}")
    
    async def send_message(self, user_id: str, text: str) -> bool:
        """Send a message to a specific user.
        
        Args:
            user_id: Telegram user ID to send message to.
            text: Message text content.
            
        Returns:
            True if message was sent successfully, False otherwise.
        """
        if not self.bot:
            logger.error("Bot not initialized, cannot send message")
            return False
        
        if not self.token:
            logger.error("Bot token not configured, cannot send message")
            return False
        
        try:
            await self.bot.send_message(chat_id=user_id, text=text)
            logger.info(f"Message sent to user {user_id}: {text[:50]}..." if len(text) > 50 else f"Message sent to user {user_id}: {text}")
            return True
        except Exception as e:
            logger.error(f"Failed to send message to user {user_id}: {e}")
            return False
    
    async def get_me(self) -> Optional[dict]:
        """Get bot information.
        
        Returns:
            Bot info dict or None if failed.
        """
        if not self.bot:
            logger.error("Bot not initialized")
            return None
        
        try:
            bot_info = await self.bot.get_me()
            logger.info(f"Bot info retrieved: @{bot_info.username}")
            return {"id": bot_info.id, "username": bot_info.username}
        except Exception as e:
            logger.error(f"Failed to get bot info: {e}")
            return None
    
    async def delete_message(self, user_id: str, message_id: int) -> bool:
        """Delete a message from a chat.
        
        Args:
            user_id: Telegram user ID (chat ID).
            message_id: ID of the message to delete.
            
        Returns:
            True if message was deleted successfully, False otherwise.
        """
        if not self.bot:
            logger.error("Bot not initialized, cannot delete message")
            return False
        
        try:
            await self.bot.delete_message(chat_id=user_id, message_id=message_id)
            logger.info(f"Message {message_id} deleted from user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete message {message_id} from user {user_id}: {e}")
            return False
    
    async def edit_message_text(self, user_id: str, message_id: int, text: str) -> bool:
        """Edit an existing message.
        
        Args:
            user_id: Telegram user ID (chat ID).
            message_id: ID of the message to edit.
            text: New message text.
            
        Returns:
            True if message was edited successfully, False otherwise.
        """
        if not self.bot:
            logger.error("Bot not initialized, cannot edit message")
            return False
        
        try:
            await self.bot.edit_message_text(text=text, chat_id=user_id, message_id=message_id)
            logger.info(f"Message {message_id} edited for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to edit message {message_id} for user {user_id}: {e}")
            return False
    
    async def stop(self) -> None:
        """Stop the bot gracefully."""
        if self.bot:
            try:
                await self.bot.session.close()
                logger.info("Telegram bot stopped gracefully")
            except Exception as e:
                logger.error(f"Error stopping bot: {e}")
        self._running = False

    async def trigger_agent_analysis(self, user_id: str) -> None:
        """Trigger agent analysis via orchestrator."""
        if self.orchestrator:
            logger.info(f"Triggering agent analysis for user {user_id}")
            await self.orchestrator.trigger_agent_analysis(user_id)
        else:
            logger.warning("No orchestrator set, cannot trigger analysis")
            if self.bot:
                await self.bot.send_message(chat_id=user_id, text="Error: Orchestrator not configured")
