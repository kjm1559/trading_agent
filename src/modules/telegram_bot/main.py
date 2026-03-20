import asyncio
import signal
import logging

from aiogram import Bot, Dispatcher

from .bot import TelegramBot
from .handlers import router, set_bot_instance
from ..shared.config import Config

logger = logging.getLogger(__name__)


async def start_bot(config: Config) -> None:
    """Start the Telegram bot."""
    bot = TelegramBot(config)
    
    if not bot.bot:
        logger.warning("Telegram bot not configured, skipping")
        return
    
    dispatcher = bot.dispatcher
    dispatcher.include_router(router)
    
    set_bot_instance(bot)
    
    bot.set_running(True)
    
    try:
        await dispatcher.start_polling(bot.token)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        await bot.stop()


def run_bot() -> None:
    """Run the Telegram bot (entry point)."""
    config = Config()
    
    if not config.telegram_bot_token:
        logger.warning("Telegram bot token not configured")
        return
    
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting Telegram bot...")
    
    try:
        asyncio.run(start_bot(config))
    except Exception as e:
        logger.error(f"Failed to run bot: {e}")