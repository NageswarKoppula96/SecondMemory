from datetime import datetime

from pydantic import BaseModel, Field


class SaveMemoryInput(BaseModel):
    content: str = Field(min_length=1)
    category: str = "OTHER"
    importance: int = Field(default=5, ge=1, le=10)


class SearchMemoriesInput(BaseModel):
    query: str = ""
    category: str | None = None


class DeleteMemoryInput(BaseModel):
    memory_id: int


class CreateTaskInput(BaseModel):
    title: str = Field(min_length=1)
    description: str | None = None
    priority: int = Field(default=5, ge=1, le=10)
    due_at: datetime | None = None


class CreateReminderInput(BaseModel):
    message: str = Field(min_length=1)
    remind_at: datetime
    recurrence: str | None = None
