from datetime import date
from typing import Literal
from pydantic import BaseModel, ConfigDict

Priority = Literal["red", "yellow", "green"]


class TopicCreate(BaseModel):
    name: str


class TopicOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    column_id: int
    topic_id: int | None = None
    priority: Priority = "green"
    due_date: date | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    topic_id: int | None = None
    priority: Priority | None = None
    due_date: date | None = None


class TaskMove(BaseModel):
    column_id: int
    position: int = 0


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    column_id: int | None
    topic_id: int | None
    topic: TopicOut | None = None
    priority: str
    position: int
    is_done: bool
    due_date: date | None


class ColumnOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    position: int
    tasks: list[TaskOut] = []

class DayUpdate(BaseModel):
    note: str | None = None
    mood_emoji: str | None = None


class DayOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    memory_date: date
    photo_path: str | None = None
    note: str | None = None
    mood_emoji: str | None = None 