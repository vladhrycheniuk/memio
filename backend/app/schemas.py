from datetime import date
from pydantic import BaseModel, ConfigDict


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    column_id: int
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
    position: int
    is_done: bool
    due_date: date | None


class ColumnOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    position: int
    tasks: list[TaskOut] = []