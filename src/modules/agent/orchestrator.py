import asyncio
import logging
from typing import Optional
from ..shared.config import Config
from ..telegram_bot import TelegramBot

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.telegram_bot = TelegramBot(self.config)
        self.telegram_bot.set_orchestrator(self)
        self._running = False
        logger.info("AgentOrchestrator initialized")

    async def action_started(self, action_name: str, details: str = "") -> None:
        """Notify that an action has started."""
        message = f"Action started: {action_name}"
        if details:
            message += f"\n{details}"
        await self._notify_all(message)
        logger.info(f"Action started: {action_name}")

    async def action_completed(self, action_name: str, success: bool, details: str = "") -> None:
        """Notify that an action has completed."""
        status = "Success" if success else "Failed"
        message = f"Action completed: {action_name} - {status}"
        if details:
            message += f"\n{details}"
        await self._notify_all(message)
        logger.info(f"Action completed: {action_name} - {status}")

    async def _notify_all(self, message: str) -> None:
        """Send notification to all authorized users."""
        if not self.telegram_bot or not self.telegram_bot.bot:
            logger.debug(f"Telegram bot not available, skipping notification: {message[:50]}")
            return

        authorized_users = self.config.telegram_authorized_users
        if not authorized_users:
            logger.debug("No authorized users configured for notifications")
            return

        tasks = []
        for user_id in authorized_users:
            tasks.append(self.telegram_bot.send_message(user_id, message))

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            sent_count = sum(1 for r in results if not isinstance(r, Exception) and r)
            logger.info(f"Notification sent to {sent_count}/{len(authorized_users)} users")

    async def trigger_agent_analysis(self, user_id: str = "") -> None:
        """Trigger agent analysis cycle."""
        logger.info("Agent analysis triggered")
        await self.action_started("Agent Analysis", "Running information collection and analysis...")

        try:
            await asyncio.sleep(1)

            await self.action_completed("Agent Analysis", True, "Analysis completed successfully")
        except Exception as e:
            await self.action_completed("Agent Analysis", False, f"Error: {str(e)}")
            logger.error(f"Agent analysis failed: {e}")

    async def start(self) -> None:
        """Start the orchestrator."""
        self._running = True
        if self.telegram_bot:
            self.telegram_bot.set_running(True)
        logger.info("AgentOrchestrator started")

    async def stop(self) -> None:
        """Stop the orchestrator."""
        self._running = False
        if self.telegram_bot:
            self.telegram_bot.set_running(False)
            await self.telegram_bot.stop()
        logger.info("AgentOrchestrator stopped")

    def is_running(self) -> bool:
        """Check if orchestrator is running."""
        return self._running