from datetime import datetime, timezone
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class MemoryCategory(StrEnum):
    WORK = "WORK"
    TECHNOLOGY = "TECHNOLOGY"
    LEARNING = "LEARNING"
    PERSONAL = "PERSONAL"
    OTHER = "OTHER"


class TaskStatus(StrEnum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Memory(Base):
    __tablename__ = "memories"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(32), default=MemoryCategory.OTHER)
    importance: Mapped[int] = mapped_column(Integer, default=5)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default=TaskStatus.PENDING)
    priority: Mapped[int] = mapped_column(Integer, default=5)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(primary_key=True)
    message: Mapped[str] = mapped_column(Text)
    remind_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    recurrence: Mapped[str | None] = mapped_column(String(32), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ReminderHistory(Base):
    __tablename__ = "reminder_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    reminder_message: Mapped[str] = mapped_column(Text)
    original_remind_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
