from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.background import BackgroundScheduler

from app.database.models import Reminder
from app.reminders.scheduler import ReminderScheduler
from app.utils import as_utc


class FakeBot:
    def __init__(self):
        self.messages = []

    def send_message(self, **kwargs):
        self.messages.append(kwargs)


def test_one_time_reminder_is_deleted_after_delivery(session):
    reminder = Reminder(message="Call John", remind_at=datetime.now(timezone.utc) + timedelta(hours=1), active=True)
    session.add(reminder)
    session.commit()
    bot = FakeBot()
    scheduler = ReminderScheduler(lambda: session, bot, 42, "UTC")
    scheduler._trigger(reminder.id)
    assert len(bot.messages) == 1
    assert session.get(Reminder, reminder.id) is None


def test_recurring_reminder_is_advanced_after_delivery(session):
    reminder = Reminder(message="Check Jenkins", remind_at=datetime.now(timezone.utc) + timedelta(hours=1), recurrence="weekly", active=True)
    session.add(reminder)
    session.commit()
    bot = FakeBot()
    scheduler = ReminderScheduler(lambda: session, bot, 42, "UTC")
    scheduler._trigger(reminder.id)
    assert as_utc(session.get(Reminder, reminder.id).remind_at) > datetime.now(timezone.utc)
    assert len(bot.messages) == 1