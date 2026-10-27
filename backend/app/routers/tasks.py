from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas

router = APIRouter(tags=["board"])

USER_ID = 1  # поки один користувач
DONE_COLUMN_TITLE = "Готово"
DEFAULT_TOPICS = {"Навчання", "Робота", "Дім", "Особисте"}


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

    task = models.Task(
        user_id=USER_ID,
        column_id=column.id,
        topic_id=data.topic_id,
        title=data.title,
        description=data.description,
        priority=data.priority,
        due_date=data.due_date,
        position=len(column.tasks),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.patch("/tasks/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, data: schemas.TaskUpdate, db: Session = Depends(get_db)):
    task = db.get(models.Task, task_id)
    if not task or task.user_id != USER_ID:
        raise HTTPException(404, "Завдання не знайдено")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
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
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(models.Task, task_id)
    if not task or task.user_id != USER_ID:
        raise HTTPException(404, "Завдання не знайдено")
    db.delete(task)
    db.commit()
    cleanup_topics(db)
    return {"ok": True}