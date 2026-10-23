from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas

router = APIRouter(tags=["board"])

USER_ID = 1  # поки один користувач
DONE_COLUMN_TITLE = "Готово"


@router.get("/board", response_model=list[schemas.ColumnOut])
def get_board(db: Session = Depends(get_db)):
    return (
        db.query(models.KanbanColumn)
        .filter_by(user_id=USER_ID)
        .order_by(models.KanbanColumn.position)
        .all()
    )


@router.post("/tasks", response_model=schemas.TaskOut)
def create_task(data: schemas.TaskCreate, db: Session = Depends(get_db)):
    column = db.get(models.KanbanColumn, data.column_id)
    if not column or column.user_id != USER_ID:
        raise HTTPException(404, "Колонку не знайдено")

    task = models.Task(
        user_id=USER_ID,
        column_id=column.id,
        title=data.title,
        description=data.description,
        due_date=data.due_date,
        position=len(column.tasks),
    )
    db.add(task)
    db.commit()
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

    # вставляємо картку на потрібне місце і перенумеровуємо колонку
    siblings = [t for t in target.tasks if t.id != task.id]
    pos = max(0, min(data.position, len(siblings)))
    task.column_id = target.id
    siblings.insert(pos, task)
    for i, t in enumerate(siblings):
        t.position = i

    # переніс у «Готово» = виконано
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
    return {"ok": True}