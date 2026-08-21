import logging

from telegram.ext import Application, CommandHandler, MessageHandler, filters

from app.config.settings import Settings
from app.database.database import build_session_factory
from app.database.init_db import init_db
from app.reminders.scheduler import ReminderScheduler
from app.telegram.handlers import help_command, memories, message, reminders, start, tasks

logger = logging.getLogger(__name__)


def build_application(settings: Settings) -> tuple[Application, ReminderScheduler]:
    init_db(settings.database_url)
    application = Application.builder().token(settings.telegram_bot_token).build()
    factory = build_session_factory(settings.database_url)
    scheduler = ReminderScheduler(factory, application.bot, settings.telegram_allowed_user_id or 0, settings.timezone)
    application.bot_data["settings"] = settings
    application.bot_data["schedule_reminder"] = scheduler.schedule
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("memories", memories))
    application.add_handler(CommandHandler("tasks", tasks))
    application.add_handler(CommandHandler("reminders", reminders))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message))
    return application, scheduler


def run_polling(settings: Settings) -> None:
    application, scheduler = build_application(settings)
    scheduler.start()
    try:
        application.run_polling()
    finally:
        scheduler.shutdown()
