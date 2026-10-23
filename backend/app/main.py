from fastapi import FastAPI
from .database import Base, engine, SessionLocal
from . import models
from .routers import tasks

Base.metadata.create_all(bind=engine)


def seed():
    """Створює користувача і 3 колонки при першому запуску."""
    db = SessionLocal()
    try:
        if not db.get(models.User, 1):
            db.add(models.User(id=1, username="me"))
            db.flush()
            for i, title in enumerate(["Зробити", "В процесі", "Готово"]):
                db.add(models.KanbanColumn(user_id=1, title=title, position=i))
            db.add(models.Streak(user_id=1))
            db.commit()
    finally:
        db.close()


seed()

app = FastAPI(title="Memio API")
app.include_router(tasks.router)


@app.get("/")
def root():
    return {"message": "Memio працює 🌊"}