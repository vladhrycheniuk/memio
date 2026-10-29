from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..recurrence import next_occurrence

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


def spawn_next(db: Session, task: models.Task):
    """Після виконання повторюваного завдання створює наступне в першій колонці."""
    today = date.today()
    nxt = next_occurrence(task.due_date or today, task.recurrence, today)
    if nxt is None:
        return
    first_col = (
        db.query(models.KanbanColumn)
        .filter_by(user_id=USER_ID)
        .order_by(models.KanbanColumn.position)
        .first()
    )
    if first_col is None:
        return
    count = db.query(models.Task).filter_by(column_id=first_col.id).count()
    db.add(models.Task(
        user_id=USER_ID,
        column_id=first_col.id,
        topic_id=task.topic_id,
        title=task.title,
        description=task.description,
        priority=task.priority,
        recurrence=task.recurrence,
        due_date=nxt,
        position=count,
        is_done=False,
        is_focus=False,
        spawned=False,
    ))
    task.spawned = True


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
    db.commit()
    db.refresh(task)
    return task


@router.patch("/tasks/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, data: schemas.TaskUpdate, db: Session = Depends(get_db)):
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

    for key, value in fields.items():
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
        if task.recurrence and not task.spawned:
            spawn_next(db, task)
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
