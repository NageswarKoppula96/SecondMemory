from datetime import datetime

from sqlalchemy.orm import Session

from app.database.models import Reminder
from app.reminders.repository import ReminderRepository
from app.utils import as_utc


class ReminderNotFoundError(LookupError):
    pass


class ReminderService:
    def __init__(self, session: Session):
        self.repository = ReminderRepository(session)

    def create(self, message: str, remind_at: datetime, recurrence: str | None = None) -> Reminder:
        if not message.strip():
            raise ValueError("Reminder message cannot be empty")
        if remind_at <= datetime.now(remind_at.tzinfo):
            raise ValueError("Reminder time must be in the future")
        if recurrence not in {None, "daily", "weekly", "monthly"}:
            raise ValueError("Recurrence must be daily, weekly, or monthly")
        return self.repository.save(Reminder(message=message.strip(), remind_at=remind_at, recurrence=recurrence))

    def get(self, reminder_id: int) -> Reminder:
        reminder = self.repository.get(reminder_id)
        if reminder is None or not reminder.active:
            raise ReminderNotFoundError(f"Reminder {reminder_id} was not found")
        return reminder

    def list_upcoming(self, now: datetime | None = None) -> list[Reminder]:
        reminders = self.repository.active()
        return [reminder for reminder in reminders if now is None or as_utc(reminder.remind_at) >= as_utc(now)]

    def cancel(self, reminder_id: int) -> None:
        self.repository.delete(self.get(reminder_id))
