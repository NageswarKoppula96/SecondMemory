from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.database.models import Task, TaskStatus
from app.tasks.repository import TaskRepository


class TaskNotFoundError(LookupError):
    pass


class TaskService:
    def __init__(self, session: Session):
        self.repository = TaskRepository(session)

    def create(self, title: str, description: str | None = None, priority: int = 5, due_at: datetime | None = None) -> Task:
        if not title.strip():
            raise ValueError("Task title cannot be empty")
        if not 1 <= priority <= 10:
            raise ValueError("Priority must be between 1 and 10")
        return self.repository.save(Task(title=title.strip(), description=description, priority=priority, due_at=due_at))

    def get(self, task_id: int) -> Task:
        task = self.repository.get(task_id)
        if task is None:
            raise TaskNotFoundError(f"Task {task_id} was not found")
        return task

    def list(self, status: str | None = None) -> list[Task]:
        return self.repository.list(status)

    def update(self, task_id: int, **changes: object) -> Task:
        task = self.get(task_id)
        for field, value in changes.items():
            if value is not None and field in {"title", "description", "priority", "due_at", "status"}:
                setattr(task, field, value)
        return self.repository.save(task)

    def complete(self, task_id: int) -> Task:
        task = self.get(task_id)
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now(timezone.utc)
        return self.repository.save(task)

    def delete(self, task_id: int) -> None:
        self.repository.delete(self.get(task_id))
