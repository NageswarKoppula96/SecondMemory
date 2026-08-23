from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from app.database.models import Memory, Reminder, Task
from app.telegram import handlers
from app.telegram.keyboards import (
    CHAT_BUTTON,
    MEMORIES_BUTTON,
    REMINDERS_BUTTON,
    TASKS_BUTTON,
    main_menu_keyboard,
)


class FakeMessage:
    def __init__(self, text=None):
        self.text = text
        self.responses = []

    async def reply_text(self, text, **kwargs):
        self.responses.append((text, kwargs))


def telegram_context(settings):
    return SimpleNamespace(bot_data={"settings": settings})


def telegram_update(text, user_id):
    return SimpleNamespace(
        effective_user=SimpleNamespace(id=user_id),
        message=FakeMessage(text),
    )


def test_main_menu_has_exact_persistent_layout():
    keyboard = main_menu_keyboard()

    assert [[button.text for button in row] for row in keyboard.keyboard] == [
        [MEMORIES_BUTTON, TASKS_BUTTON],
        [REMINDERS_BUTTON, CHAT_BUTTON],
    ]
    assert keyboard.resize_keyboard is True
    assert keyboard.is_persistent is True


@pytest.mark.asyncio
async def test_start_displays_main_menu():
    settings = SimpleNamespace(telegram_allowed_user_id=42)
    update = telegram_update("/start", 42)

    await handlers.start(update, telegram_context(settings))

    text, options = update.message.responses[0]
    assert text.startswith("Welcome to SecondMemory.")
    assert options["reply_markup"].keyboard[0][0].text == MEMORIES_BUTTON


@pytest.mark.asyncio
async def test_memories_menu_reads_service_without_invoking_agent(session, monkeypatch):
    session.add(Memory(content="Learn LangGraph", is_active=True))
    session.commit()
    settings = SimpleNamespace(
        telegram_allowed_user_id=42,
        database_url="sqlite://",
    )
    update = telegram_update(MEMORIES_BUTTON, 42)
    monkeypatch.setattr(handlers, "session_factory", lambda settings: lambda: session)

    def fail_if_called(*args, **kwargs):
        raise AssertionError("menu button must not invoke AssistantAgent")

    monkeypatch.setattr(handlers.AssistantAgent, "invoke", fail_if_called)
    await handlers.message(update, telegram_context(settings))

    assert "🧠 Your Memories" in update.message.responses[0][0]
    assert "Learn LangGraph" in update.message.responses[0][0]


@pytest.mark.asyncio
async def test_tasks_and_reminders_menu_use_direct_services(session, monkeypatch):
    session.add(Task(title="Prepare interview questions", status="PENDING"))
    session.add(
        Reminder(
            message="Call John",
            remind_at=datetime.now(timezone.utc) + timedelta(minutes=5),
            active=True,
        )
    )
    session.commit()
    settings = SimpleNamespace(telegram_allowed_user_id=42, database_url="sqlite://")
    monkeypatch.setattr(handlers, "session_factory", lambda settings: lambda: session)

    for button, expected in (
        (TASKS_BUTTON, "Prepare interview questions"),
        (REMINDERS_BUTTON, "Call John"),
    ):
        update = telegram_update(button, 42)
        await handlers.message(update, telegram_context(settings))
        assert expected in update.message.responses[0][0]


@pytest.mark.asyncio
async def test_chat_button_replies_without_replacing_ai_agent():
    settings = SimpleNamespace(telegram_allowed_user_id=42)
    update = telegram_update(CHAT_BUTTON, 42)

    await handlers.message(update, telegram_context(settings))

    assert update.message.responses[0][0].startswith("🤖 Chat mode enabled.")