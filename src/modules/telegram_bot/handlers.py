from typing import TYPE_CHECKING

from aiogram import Router
from aiogram.types import Message

if TYPE_CHECKING:
    from .bot import TelegramBot

import logging

logger = logging.getLogger(__name__)


router = Router()


def set_bot_instance(bot: "TelegramBot") -> None:
    """Set the global bot instance for handlers."""
    router.bot_instance = bot


def get_bot_instance() -> "TelegramBot | None":
    """Get the global bot instance."""
    return getattr(router, "bot_instance", None)


@router.message(lambda msg: msg.text == "/start")
async def cmd_start(message: Message) -> None:
    """Handle /start command."""
    bot = get_bot_instance()
    if not bot or not bot.is_authorized(str(message.from_user.id)):
        await message.answer("Unauthorized access")
        return

    response = "Trading Agent Bot\n\n"
    response += "Available commands:\n"
    response += "/start - This menu\n"
    response += "/status - Bot status\n"
    response += "/check - Trigger agent analysis\n"
    response += "/help - Help message\n\n"
    response += "Type /check to run agent analysis"

    await message.answer(response)


@router.message(lambda msg: msg.text == "/status")
async def cmd_status(message: Message) -> None:
    """Handle /status command."""
    bot = get_bot_instance()
    if not bot or not bot.is_authorized(str(message.from_user.id)):
        await message.answer("Unauthorized access")
        return

    running = "Running" if bot.is_running() else "Stopped"
    paused = "Paused" if bot.is_paused() else "Active"

    response = "Bot Status\n\n"
    response += f"Status: {running}\n"
    response += f"Activity: {paused}"

    await message.answer(response)


@router.message(lambda msg: msg.text == "/help")
async def cmd_help(message: Message) -> None:
    """Handle /help command."""
    bot = get_bot_instance()
    if not bot or not bot.is_authorized(str(message.from_user.id)):
        await message.answer("Unauthorized access")
        return

    response = "Help\n\n"
    response += "Trading Agent Commands:\n\n"
    response += "/start - Show welcome message and commands\n"
    response += "/status - Check bot status\n"
    response += "/check - Trigger agent analysis cycle\n"
    response += "/help - Show this help message\n\n"
    response += "Notifications\n"
    response += "You will receive notifications when:\n"
    response += "- Agent actions start\n"
    response += "- Agent actions complete\n"
    response += "- Trading operations execute\n"
    response += "- Errors occur"

    await message.answer(response)


@router.message(lambda msg: msg.text == "/check")
async def cmd_check(message: Message) -> None:
    """Handle /check command - triggers agent analysis."""
    bot = get_bot_instance()
    if not bot or not bot.is_authorized(str(message.from_user.id)):
        await message.answer("Unauthorized access")
        return

    await message.answer("Starting agent analysis...")
    logger.info("Agent analysis triggered via Telegram")
    if hasattr(bot, "trigger_agent_analysis"):
        await bot.trigger_agent_analysis(message.from_user.id)
