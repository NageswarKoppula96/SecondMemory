import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.ai.agent import AssistantAgent
from app.ai.tools import build_tools
from app.config.settings import Settings
from app.database.database import build_session_factory
from app.memory.service import MemoryNotFoundError

logger = logging.getLogger(__name__)


def authorized(update: Update, settings: Settings) -> bool:
    user = update.effective_user
    return bool(user and settings.telegram_allowed_user_id and user.id == settings.telegram_allowed_user_id)


def session_factory(settings: Settings):
    return build_session_factory(settings.database_url)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.bot_data["settings"]
    if not authorized(update, settings):
        return
    await update.message.reply_text("Welcome to SecondMemory. Tell me what to remember, do, or remind you about.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.bot_data["settings"]
    if not authorized(update, settings):
        return
    await update.message.reply_text("Use natural language, or /memories, /tasks, and /reminders for quick lists.")


async def direct_list(update: Update, context: ContextTypes.DEFAULT_TYPE, kind: str) -> None:
    settings: Settings = context.bot_data["settings"]
    if not authorized(update, settings):
        return
    with session_factory(settings)() as session:
        if kind == "memories":
            from app.memory.service import MemoryService
            text = "\n".join(f"{memory.id}. {memory.content}" for memory in MemoryService(session).search()) or "No memories found."
        elif kind == "tasks":
            from app.tasks.service import TaskService
            text = "\n".join(f"{task.id}. [{task.status}] {task.title}" for task in TaskService(session).list()) or "No tasks found."
        else:
            from app.reminders.service import ReminderService
            text = "\n".join(f"{item.id}. {item.remind_at:%Y-%m-%d %H:%M} {item.message}" for item in ReminderService(session).list_upcoming()) or "No upcoming reminders."
    await update.message.reply_text(text)


async def memories(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await direct_list(update, context, "memories")


async def tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await direct_list(update, context, "tasks")


async def reminders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await direct_list(update, context, "reminders")


async def message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.bot_data["settings"]
    if not authorized(update, settings) or not update.message or not update.message.text:
        return
    try:
        with session_factory(settings)() as session:
            tools = build_tools(session, context.bot_data.get("schedule_reminder"))
            response = AssistantAgent(settings).invoke(update.message.text, tools)
        await update.message.reply_text(response)
    except Exception:
        logger.exception("Failed to process Telegram message")
        await update.message.reply_text("I couldn't process that request. Please check the server configuration and try again.")
