from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Task, TaskStatus


class TaskRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, task: Task) -> Task:
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def get(self, task_id: int) -> Task | None:
        return self.session.get(Task, task_id)

    def list(self, status: str | None = None) -> list[Task]:
        statement = select(Task)
        if status:
            statement = statement.where(Task.status == status)
        return list(self.session.scalars(statement.order_by(Task.due_at.asc().nullslast(), Task.created_at.desc())))

    def delete(self, task: Task) -> None:
        self.session.delete(task)
        self.session.commit()
