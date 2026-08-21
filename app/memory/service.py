from sqlalchemy.orm import Session

from app.database.models import Memory, MemoryCategory
from app.memory.repository import MemoryRepository


class MemoryNotFoundError(LookupError):
    pass


class MemoryService:
    def __init__(self, session: Session):
        self.repository = MemoryRepository(session)

    def save(self, content: str, category: str = MemoryCategory.OTHER, importance: int = 5) -> Memory:
        if not content.strip():
            raise ValueError("Memory content cannot be empty")
        if not 1 <= importance <= 10:
            raise ValueError("Importance must be between 1 and 10")
        return self.repository.save(Memory(content=content.strip(), category=category, importance=importance))

    def get(self, memory_id: int) -> Memory:
        memory = self.repository.get(memory_id)
        if memory is None or not memory.is_active:
            raise MemoryNotFoundError(f"Memory {memory_id} was not found")
        return memory

    def search(self, query: str = "", category: str | None = None) -> list[Memory]:
        return self.repository.search(query.strip(), category)

    def update(self, memory_id: int, content: str | None = None, category: str | None = None, importance: int | None = None) -> Memory:
        memory = self.get(memory_id)
        if content is not None:
            if not content.strip():
                raise ValueError("Memory content cannot be empty")
            memory.content = content.strip()
        if category is not None:
            memory.category = category
        if importance is not None:
            if not 1 <= importance <= 10:
                raise ValueError("Importance must be between 1 and 10")
            memory.importance = importance
        return self.repository.save(memory)

    def delete(self, memory_id: int) -> None:
        self.repository.delete(self.get(memory_id))
