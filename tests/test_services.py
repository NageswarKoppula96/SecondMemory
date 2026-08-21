from datetime import datetime, timedelta, timezone

import pytest

from app.memory.service import MemoryNotFoundError, MemoryService
from app.reminders.service import ReminderService
from app.tasks.service import TaskService
from app.utils import next_occurrence


def test_memory_lifecycle(session):
    service = MemoryService(session)
    memory = service.save("Production uses Java 21", "WORK", 8)
    assert service.search("java")[0].id == memory.id
    service.update(memory.id, content="Production uses Java 25")
    assert service.get(memory.id).content.endswith("25")
    service.delete(memory.id)
    assert service.search("java") == []
    with pytest.raises(MemoryNotFoundError):
        service.get(memory.id)


def test_task_lifecycle(session):
    service = TaskService(session)
    task = service.create("Upgrade Java", priority=2)
    service.update(task.id, description="Upgrade production")
    completed = service.complete(task.id)
    assert completed.status == "COMPLETED"
    assert service.list("COMPLETED")[0].id == task.id
    service.delete(task.id)
    assert service.list() == []


def test_reminder_lifecycle_and_recurrence(session):
    service = ReminderService(session)
    when = datetime.now(timezone.utc) + timedelta(hours=1)
    reminder = service.create("Check Jenkins", when, "weekly")
    assert service.list_upcoming()[0].id == reminder.id
    service.cancel(reminder.id)
    assert service.list_upcoming() == []
    assert next_occurrence(when, "weekly") == when + timedelta(weeks=1)


def test_past_reminder_is_rejected(session):
    with pytest.raises(ValueError):
        ReminderService(session).create("Too late", datetime.now(timezone.utc) - timedelta(minutes=1))
