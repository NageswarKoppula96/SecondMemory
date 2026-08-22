import logging
import asyncio
import inspect
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.base import JobLookupError
from sqlalchemy.orm import sessionmaker

from app.database.models import Reminder
from app.reminders.repository import ReminderRepository
from app.utils import as_utc, next_occurrence

logger = logging.getLogger(__name__)


class ReminderScheduler:
    def __init__(self, session_factory: sessionmaker, bot, chat_id: int, timezone: str):
        self.session_factory = session_factory
        self.bot = bot
        self.chat_id = chat_id
        self.timezone = ZoneInfo(timezone)
        self.scheduler = BackgroundScheduler(timezone=self.timezone)

    def restore(self) -> int:
        with self.session_factory() as session:
            reminders = ReminderRepository(session).active()
        for reminder in reminders:
            self.schedule(reminder)
        logger.info("Restored %d active reminders", len(reminders))
        return len(reminders)

    def schedule(self, reminder: Reminder) -> None:
        self.scheduler.add_job(
            self._trigger,
            trigger=DateTrigger(run_date=reminder.remind_at, timezone=self.timezone),
            args=[reminder.id],
            id=f"reminder-{reminder.id}",
            replace_existing=True,
        )

    def start(self) -> None:
        self.restore()
        self.scheduler.start()

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

    def cancel(self, reminder_id: int) -> None:
        try:
            self.scheduler.remove_job(f"reminder-{reminder_id}")
        except JobLookupError:
            logger.debug("Reminder %s was not scheduled", reminder_id)

    def _trigger(self, reminder_id: int) -> None:
        with self.session_factory() as session:
            repository = ReminderRepository(session)
            reminder = repository.get(reminder_id)
            if reminder is None or not reminder.active:
                return
            message = reminder.message
            original_time = reminder.remind_at
            try:
                result = self.bot.send_message(chat_id=self.chat_id, text=f"🔔 Reminder: {message}")
                if inspect.isawaitable(result):
                    asyncio.run(result)
            except Exception:
                logger.exception("Failed to deliver reminder %s", reminder_id)
                return
            now = datetime.now(self.timezone)
            repository.add_history(reminder, now)
            if reminder.recurrence:
                reminder.remind_at = next_occurrence(as_utc(reminder.remind_at), reminder.recurrence)
                repository.save(reminder)
                self.schedule(reminder)
            else:
                repository.delete(reminder)
            logger.info("Triggered reminder %s scheduled for %s", reminder_id, original_time)
