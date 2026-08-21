from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Memory


class MemoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, memory: Memory) -> Memory:
        self.session.add(memory)
        self.session.commit()
        self.session.refresh(memory)
        return memory

    def get(self, memory_id: int) -> Memory | None:
        return self.session.get(Memory, memory_id)

    def search(self, query: str = "", category: str | None = None) -> list[Memory]:
        statement = select(Memory).where(Memory.is_active.is_(True))
        if query:
            statement = statement.where(Memory.content.ilike(f"%{query}%"))
        if category:
            statement = statement.where(Memory.category == category)
        return list(self.session.scalars(statement.order_by(Memory.created_at.desc())))

    def delete(self, memory: Memory) -> None:
        memory.is_active = False
        self.session.commit()
