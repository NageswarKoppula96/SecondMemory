from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Reminder, ReminderHistory


class ReminderRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, reminder: Reminder) -> Reminder:
        self.session.add(reminder)
        self.session.commit()
        self.session.refresh(reminder)
        return reminder

    def get(self, reminder_id: int) -> Reminder | None:
        return self.session.get(Reminder, reminder_id)

    def active(self, before: datetime | None = None) -> list[Reminder]:
        statement = select(Reminder).where(Reminder.active.is_(True))
        if before:
            statement = statement.where(Reminder.remind_at <= before)
        return list(self.session.scalars(statement.order_by(Reminder.remind_at.asc())))

    def delete(self, reminder: Reminder) -> None:
        self.session.delete(reminder)
        self.session.commit()

    def add_history(self, reminder: Reminder, triggered_at: datetime) -> None:
        self.session.add(ReminderHistory(reminder_message=reminder.message, original_remind_at=reminder.remind_at, triggered_at=triggered_at))
        self.session.commit()
