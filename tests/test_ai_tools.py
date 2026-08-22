from datetime import datetime, timedelta, timezone

from app.ai.tools import build_tools
from app.database.models import Memory, Reminder


def test_build_tools_creates_all_tools(session):
    tools = build_tools(session)

    assert [tool.name for tool in tools] == [
        "save_memory",
        "search_memories",
        "list_memories",
        "delete_memory",
        "create_task",
        "list_tasks",
        "complete_task",
        "delete_task",
        "create_reminder",
        "list_upcoming_reminders",
        "cancel_reminder",
    ]
    assert all(tool.description for tool in tools)


def test_delete_memory_by_id_and_handle_missing_memory(session):
    tools = {tool.name: tool for tool in build_tools(session)}
    memory = Memory(content="Production uses Java 21", is_active=True)
    session.add(memory)
    session.commit()

    assert tools["delete_memory"].invoke({"memory_id": memory.id}) == f"Memory {memory.id} deleted."
    assert session.get(Memory, memory.id).is_active is False
    assert tools["delete_memory"].invoke({"memory_id": memory.id}) == f"Memory {memory.id} was not found."


def test_cancel_reminder_by_id_and_remove_scheduled_job(session):
    reminder = Reminder(
        message="Check SecondMemory",
        remind_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        active=True,
    )
    session.add(reminder)
    session.commit()

    cancelled = []
    tools = {
        tool.name: tool
        for tool in build_tools(session, cancel_reminder_schedule=cancelled.append)
    }

    assert tools["cancel_reminder"].invoke({"reminder_id": reminder.id}) == f"Reminder {reminder.id} cancelled."
    assert cancelled == [reminder.id]
    assert session.get(Reminder, reminder.id) is None
    assert tools["cancel_reminder"].invoke({"reminder_id": reminder.id}) == f"Reminder {reminder.id} was not found."