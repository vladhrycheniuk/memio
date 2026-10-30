import uuid
from datetime import date, datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..recurrence import occurrences

Scope = Literal["this", "future", "all"]
SHARED_FIELDS = ("title", "description", "topic_id", "priority")  # поширюються на серію

router = APIRouter(tags=["board"])

USER_ID = 1  # поки один користувач
DONE_COLUMN_TITLE = "Готово"
DEFAULT_TOPICS = {"Навчання", "Робота", "Дім", "Особисте"}
MAX_FOCUS = 3  # «головне на день»


def cleanup_topics(db: Session):
    """Видаляє власні теми, у яких не лишилось жодного завдання."""
    used = {
        tid for (tid,) in db.query(models.Task.topic_id)
        .filter(models.Task.topic_id.isnot(None))
        .distinct()
    }
    for topic in db.query(models.Topic).filter_by(user_id=USER_ID).all():
        if topic.name not in DEFAULT_TOPICS and topic.id not in used:
            db.delete(topic)
    db.commit()


def check_focus_limit(db: Session, due, exclude_id=None):
    """Не більше MAX_FOCUS «головних» завдань на одну дату."""
    query = db.query(models.Task).filter(
        models.Task.user_id == USER_ID,
        models.Task.is_focus.is_(True),
    )
    if due is None:
        query = query.filter(models.Task.due_date.is_(None))
    else:
        query = query.filter(models.Task.due_date == due)
    if exclude_id is not None:
        query = query.filter(models.Task.id != exclude_id)
    if query.count() >= MAX_FOCUS:
        raise HTTPException(400, "focus_limit")


def first_column(db: Session):
    return (
        db.query(models.KanbanColumn)
        .filter_by(user_id=USER_ID)
        .order_by(models.KanbanColumn.position)
        .first()
    )


def make_series(db: Session, task: models.Task, rule: str, until):
    """Перетворює завдання на серію: створює всі повтори до дати until одразу."""
    start = task.due_date or date.today()
    task.due_date = start
    until = until or date(start.year, 12, 31)

    series_id = uuid.uuid4().hex
    task.series_id = series_id
    task.recurrence = rule

    column = first_column(db)
    if column is None:
        return
    position = db.query(models.Task).filter_by(column_id=column.id).count()
    for i, day in enumerate(occurrences(start, rule, until)[1:]):
        db.add(models.Task(
            user_id=USER_ID,
            column_id=column.id,
            topic_id=task.topic_id,
            title=task.title,
            description=task.description,
            priority=task.priority,
            recurrence=rule,
            series_id=series_id,
            due_date=day,
            position=position + i,
            is_done=False,
            is_focus=False,
        ))


def series_rows(db: Session, task: models.Task, scope: str):
    """Які завдання зачепить дія: лише це, це й наступні або вся серія."""
    if not task.series_id or scope == "this":
        return [task]
    query = db.query(models.Task).filter(
        models.Task.user_id == USER_ID,
        models.Task.series_id == task.series_id,
    )
    if scope == "future":
        if task.due_date is None:
            return [task]
        query = query.filter(models.Task.due_date >= task.due_date)
    return query.all()


# ---------- теми ----------
@router.get("/topics", response_model=list[schemas.TopicOut])
def get_topics(db: Session = Depends(get_db)):
    cleanup_topics(db)
    return db.query(models.Topic).filter_by(user_id=USER_ID).order_by(models.Topic.id).all()


@router.post("/topics", response_model=schemas.TopicOut)
def create_topic(data: schemas.TopicCreate, db: Session = Depends(get_db)):
    name = data.name.strip()
    if not name:
        raise HTTPException(400, "Порожня назва")
    existing = db.query(models.Topic).filter_by(user_id=USER_ID, name=name).first()
    if existing:
        return existing
    topic = models.Topic(user_id=USER_ID, name=name)
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic


# ---------- дошка ----------
@router.get("/board", response_model=list[schemas.ColumnOut])
def get_board(db: Session = Depends(get_db)):
    return (
        db.query(models.KanbanColumn)
        .filter_by(user_id=USER_ID)
        .order_by(models.KanbanColumn.position)
        .all()
    )


# ---------- завдання ----------
@router.post("/tasks", response_model=schemas.TaskOut)
def create_task(data: schemas.TaskCreate, db: Session = Depends(get_db)):
    column = db.get(models.KanbanColumn, data.column_id)
    if not column or column.user_id != USER_ID:
        raise HTTPException(404, "Колонку не знайдено")

    if data.is_focus:
        check_focus_limit(db, data.due_date)

    task = models.Task(
        user_id=USER_ID,
        column_id=column.id,
        topic_id=data.topic_id,
        title=data.title,
        description=data.description,
        priority=data.priority,
        due_date=data.due_date,
        recurrence=data.recurrence,
        is_focus=data.is_focus,
        position=len(column.tasks),
    )
    db.add(task)
    db.flush()
    if data.recurrence:
        make_series(db, task, data.recurrence, data.repeat_until)
    db.commit()
    db.refresh(task)
    return task


@router.patch("/tasks/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, data: schemas.TaskUpdate, scope: Scope = "this",
                db: Session = Depends(get_db)):
    task = db.get(models.Task, task_id)
    if not task or task.user_id != USER_ID:
        raise HTTPException(404, "Завдання не знайдено")

    fields = data.model_dump(exclude_unset=True)
    if fields.get("is_focus", True) is None:
        fields.pop("is_focus")

    new_focus = fields.get("is_focus", task.is_focus)
    new_due = fields["due_date"] if "due_date" in fields else task.due_date
    if new_focus and ("is_focus" in fields or "due_date" in fields):
        check_focus_limit(db, new_due, exclude_id=task.id)

    has_recurrence = "recurrence" in fields
    recurrence = fields.pop("recurrence", None)
    repeat_until = fields.pop("repeat_until", None)

    # назву, опис, тему й пріоритет можна застосувати до всієї серії або її частини
    shared = {key: fields.pop(key) for key in SHARED_FIELDS if key in fields}
    for row in series_rows(db, task, scope):
        for key, value in shared.items():
            setattr(row, key, value)
    # дата й «головне» стосуються лише цього завдання
    for key, value in fields.items():
        setattr(task, key, value)

    # правило повтору можна задати лише завданню, яке ще не є частиною серії
    if has_recurrence and task.series_id is None:
        if recurrence:
            make_series(db, task, recurrence, repeat_until)
        else:
            task.recurrence = None
    db.commit()
    cleanup_topics(db)
    db.refresh(task)
    return task


@router.patch("/tasks/{task_id}/move", response_model=schemas.TaskOut)
def move_task(task_id: int, data: schemas.TaskMove, db: Session = Depends(get_db)):
    task = db.get(models.Task, task_id)
    if not task or task.user_id != USER_ID:
        raise HTTPException(404, "Завдання не знайдено")

    target = db.get(models.KanbanColumn, data.column_id)
    if not target or target.user_id != USER_ID:
        raise HTTPException(404, "Колонку не знайдено")

    siblings = [t for t in target.tasks if t.id != task.id]
    pos = max(0, min(data.position, len(siblings)))
    task.column_id = target.id
    siblings.insert(pos, task)
    for i, t in enumerate(siblings):
        t.position = i

    was_done = task.is_done
    task.is_done = target.title == DONE_COLUMN_TITLE
    if task.is_done and not was_done:
        task.completed_at = datetime.utcnow()
    elif not task.is_done:
        task.completed_at = None

    db.commit()
    db.refresh(task)
    return task


@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, scope: Scope = "this", db: Session = Depends(get_db)):
    task = db.get(models.Task, task_id)
    if not task or task.user_id != USER_ID:
        raise HTTPException(404, "Завдання не знайдено")
    for row in series_rows(db, task, scope):
        db.delete(row)
    db.commit()
    cleanup_topics(db)
    return {"ok": True}
