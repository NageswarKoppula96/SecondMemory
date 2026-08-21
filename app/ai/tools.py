from datetime import datetime

from langchain_core.tools import StructuredTool
from sqlalchemy.orm import Session

from app.ai.schemas import (
    CreateReminderInput,
    CreateTaskInput,
    SaveMemoryInput,
    SearchMemoriesInput,
)
from app.memory.service import MemoryService
from app.reminders.service import ReminderService
from app.tasks.service import TaskService


def build_tools(
    session: Session,
    schedule_reminder=None,
) -> list[StructuredTool]:
    memories = MemoryService(session)
    tasks = TaskService(session)
    reminders = ReminderService(session)

    def save_memory(
        content: str,
        category: str = "OTHER",
        importance: int = 5,
    ) -> str:
        memory = memories.save(
            content=content,
            category=category,
            importance=importance,
        )
        return f"Memory saved with id {memory.id}."

    def search_memories(
        query: str = "",
        category: str | None = None,
    ) -> str:
        found = memories.search(
            query=query,
            category=category,
        )

        return (
            "\n".join(
                f"{memory.id}: {memory.content}"
                for memory in found
            )
            or "No memories found."
        )

    def list_memories() -> str:
        return search_memories()

    def create_task(
        title: str,
        description: str | None = None,
        priority: int = 5,
        due_at: datetime | None = None,
    ) -> str:
        task = tasks.create(
            title=title,
            description=description,
            priority=priority,
            due_at=due_at,
        )
        return f"Task created with id {task.id}: {task.title}"

    def list_tasks(status: str | None = None) -> str:
        found = tasks.list(status)

        return (
            "\n".join(
                f"{task.id}: [{task.status}] {task.title}"
                for task in found
            )
            or "No tasks found."
        )

    def complete_task(task_id: int) -> str:
        task = tasks.complete(task_id)
        return f"Task completed: {task.title}"

    def delete_task(task_id: int) -> str:
        tasks.delete(task_id)
        return "Task deleted."

    def create_reminder(
        message: str,
        remind_at: datetime,
        recurrence: str | None = None,
    ) -> str:
        reminder = reminders.create(
            message=message,
            remind_at=remind_at,
            recurrence=recurrence,
        )

        if schedule_reminder:
            schedule_reminder(reminder)

        return f"Reminder created with id {reminder.id}."

    def list_upcoming_reminders() -> str:
        found = reminders.list_upcoming()

        return (
            "\n".join(
                f"{reminder.id}: "
                f"{reminder.remind_at:%Y-%m-%d %H:%M} "
                f"{reminder.message}"
                for reminder in found
            )
            or "No upcoming reminders."
        )

    def cancel_reminder(reminder_id: int) -> str:
        reminders.cancel(reminder_id)
        return "Reminder cancelled."

    return [
        StructuredTool.from_function(
            save_memory,
            name="save_memory",
            description=(
                "Save important information provided by the user "
                "as a long-term memory. Use this when the user "
                "explicitly asks to remember, save, or store information."
            ),
            args_schema=SaveMemoryInput,
        ),
        StructuredTool.from_function(
            search_memories,
            name="search_memories",
            description=(
                "Search the user's saved memories and return "
                "information relevant to the user's question."
            ),
            args_schema=SearchMemoriesInput,
        ),
        StructuredTool.from_function(
            list_memories,
            name="list_memories",
            description=(
                "List all of the user's saved memories. "
                "Use this when the user asks to show or list memories."
            ),
        ),
        StructuredTool.from_function(
            create_task,
            name="create_task",
            description=(
                "Create a task representing something "
                "the user needs to do."
            ),
            args_schema=CreateTaskInput,
        ),
        StructuredTool.from_function(
            list_tasks,
            name="list_tasks",
            description=(
                "List the user's tasks, optionally filtered by status."
            ),
        ),
        StructuredTool.from_function(
            complete_task,
            name="complete_task",
            description="Mark an existing task as completed.",
        ),
        StructuredTool.from_function(
            delete_task,
            name="delete_task",
            description="Delete an existing task.",
        ),
        StructuredTool.from_function(
            create_reminder,
            name="create_reminder",
            description=(
                "Create a future reminder that sends the user "
                "a Telegram notification at the specified date and time."
            ),
            args_schema=CreateReminderInput,
        ),
        StructuredTool.from_function(
            list_upcoming_reminders,
            name="list_upcoming_reminders",
            description=(
                "List the user's active future reminders "
                "in chronological order."
            ),
        ),
        StructuredTool.from_function(
            cancel_reminder,
            name="cancel_reminder",
            description="Cancel an active future reminder.",
        ),
    ]