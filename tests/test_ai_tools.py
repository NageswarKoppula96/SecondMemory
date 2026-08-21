from app.ai.tools import build_tools


def test_build_tools_creates_all_tools(session):
    tools = build_tools(session)

    assert [tool.name for tool in tools] == [
        "save_memory",
        "search_memories",
        "list_memories",
        "create_task",
        "list_tasks",
        "complete_task",
        "delete_task",
        "create_reminder",
        "list_upcoming_reminders",
        "cancel_reminder",
    ]
    assert all(tool.description for tool in tools)