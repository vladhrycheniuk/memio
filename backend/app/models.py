from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Boolean, Date, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    columns = relationship("KanbanColumn", back_populates="user", cascade="all, delete")
    tasks = relationship("Task", back_populates="user", cascade="all, delete")
    topics = relationship("Topic", back_populates="user", cascade="all, delete")
    streak = relationship("Streak", back_populates="user", uselist=False, cascade="all, delete")
    memories = relationship("DailyMemory", back_populates="user", cascade="all, delete")


class KanbanColumn(Base):
    __tablename__ = "kanban_columns"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(100), nullable=False)
    position = Column(Integer, default=0)

    user = relationship("User", back_populates="columns")
    tasks = relationship("Task", back_populates="column", order_by="Task.position")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(50), nullable=False)

    user = relationship("User", back_populates="topics")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    column_id = Column(Integer, ForeignKey("kanban_columns.id"), nullable=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String(10), default="green")  # red / yellow / green
    position = Column(Integer, default=0)
    due_date = Column(Date, nullable=True)
    is_done = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # повтор: daily / weekdays / weekly / monthly (або NULL)
    recurrence = Column(String(10), nullable=True)
    # «головне на день»: не більше трьох на одну дату
    is_focus = Column(Boolean, default=False)
    # чи вже створено наступний повтор (щоб не дублювати)
    spawned = Column(Boolean, default=False)

    user = relationship("User", back_populates="tasks")
    column = relationship("KanbanColumn", back_populates="tasks")
    topic = relationship("Topic")


class Streak(Base):
    __tablename__ = "streaks"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_active_date = Column(Date, nullable=True)
    freeze_days_available = Column(Integer, default=2)

    user = relationship("User", back_populates="streak")


class DailyMemory(Base):
    __tablename__ = "daily_memories"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    memory_date = Column(Date, default=date.today)
    photo_path = Column(String(300), nullable=True)
    note = Column(String(280), nullable=True)
    mood_emoji = Column(String(8), nullable=True)

    user = relationship("User", back_populates="memories")
