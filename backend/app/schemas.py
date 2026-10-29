from datetime import date
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

Priority = Literal["red", "yellow", "green"]
Recurrence = Literal["daily", "weekdays", "weekly", "monthly"]


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
    recurrence: Recurrence | None = None
    is_focus: bool = False


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    topic_id: int | None = None
    priority: Priority | None = None
    due_date: date | None = None
    recurrence: Recurrence | None = None
    is_focus: bool | None = None


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
    recurrence: str | None = None
    is_focus: bool | None = False


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


class PrintRequest(BaseModel):
    year: int = Field(ge=1900, le=2200)
    month: int = Field(ge=1, le=12)
    format: Literal["png", "pdf"] = "pdf"
    orientation: Literal["portrait", "landscape"] = "portrait"
    language: Literal["uk", "en", "sv"] = "uk"
    frame_style: Literal["none", "line", "double", "rounded", "dashed"] = "line"
    frame_color: str = Field(default="#9CCBEA", pattern=r"^#[0-9a-fA-F]{6}$")
    frame_width: Literal["thin", "medium", "thick"] = "medium"
    corners: Literal["round", "square"] = "round"
    show_logo: bool = True
    preview: bool = False
