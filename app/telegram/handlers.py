import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.ai.agent import AssistantAgent
from app.ai.tools import build_tools
from app.config.settings import Settings
from app.database.database import build_session_factory

logger = logging.getLogger(__name__)


def is_quota_exhausted(error: Exception) -> bool:
    """
    Check whether an exception is caused by an API quota/rate-limit issue.
    """
    error_text = str(error).upper()

    status_code = (
        getattr(error, "code", None)
        or getattr(error, "status_code", None)
    )

    return (
        status_code == 429
        or "RESOURCE_EXHAUSTED" in error_text
        or ("429" in error_text and "QUOTA" in error_text)
    )


def authorized(update: Update, settings: Settings) -> bool:
    """
    Check whether the Telegram user is authorized to use the bot.
    """
    user = update.effective_user

    return bool(
        user
        and settings.telegram_allowed_user_id
        and user.id == settings.telegram_allowed_user_id
    )


def session_factory(settings: Settings):
    """
    Create the database session factory.
    """
    return build_session_factory(settings.database_url)


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    Handle /start command.
    """
    settings: Settings = context.bot_data["settings"]

    if not authorized(update, settings):
        return

    await update.message.reply_text(
        "Welcome to SecondMemory. "
        "Tell me what to remember, do, or remind you about."
    )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    Handle /help command.
    """
    settings: Settings = context.bot_data["settings"]

    if not authorized(update, settings):
        return

    await update.message.reply_text(
        "Use natural language, or /memories, /tasks, "
        "and /reminders for quick lists."
    )


async def direct_list(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    kind: str,
) -> None:
    """
    Handle direct list commands such as memories, tasks, and reminders.
    """
    settings: Settings = context.bot_data["settings"]

    if not authorized(update, settings):
        return

    with session_factory(settings)() as session:
        if kind == "memories":
            from app.memory.service import MemoryService

            text = (
                "\n".join(
                    f"{memory.id}. {memory.content}"
                    for memory in MemoryService(session).search()
                )
                or "No memories found."
            )

        elif kind == "tasks":
            from app.tasks.service import TaskService

            text = (
                "\n".join(
                    f"{task.id}. [{task.status}] {task.title}"
                    for task in TaskService(session).list()
                )
                or "No tasks found."
            )

        else:
            from app.reminders.service import ReminderService

            text = (
                "\n".join(
                    f"{item.id}. "
                    f"{item.remind_at:%Y-%m-%d %H:%M} "
                    f"{item.message}"
                    for item in ReminderService(session).list_upcoming()
                )
                or "No upcoming reminders."
            )

    await update.message.reply_text(text)


async def memories(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    Handle /memories command.
    """
    await direct_list(update, context, "memories")


async def tasks(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    Handle /tasks command.
    """
    await direct_list(update, context, "tasks")


async def reminders(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    Handle /reminders command.
    """
    await direct_list(update, context, "reminders")


async def message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    Process natural-language Telegram messages using the AI assistant.
    """
    settings: Settings = context.bot_data["settings"]

    if (
        not authorized(update, settings)
        or not update.message
        or not update.message.text
    ):
        return

    try:
        with session_factory(settings)() as session:
            tools = build_tools(
                session,
                context.bot_data.get("schedule_reminder"),
            )

            response = AssistantAgent(settings).invoke(
                update.message.text,
                tools,
            )

        await update.message.reply_text(response)

    except Exception as error:
        logger.exception("Failed to process Telegram message")

        if is_quota_exhausted(error):
            await update.message.reply_text(
                "Gemini API quota has been exceeded. "
                "Please try again later or check your Gemini API quota."
            )
        else:
            await update.message.reply_text(
                "I couldn't process that request. "
                "Please check the server configuration and try again."
            )