from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .database import Base, engine, SessionLocal
from . import models
from .routers import tasks, days, export

Base.metadata.create_all(bind=engine)


def seed():
    """Створює користувача, колонки й теми при першому запуску."""
    db = SessionLocal()
    try:
        if not db.get(models.User, 1):
            db.add(models.User(id=1, username="me"))
            db.flush()
            for i, title in enumerate(["Зробити", "В процесі", "Готово"]):
                db.add(models.KanbanColumn(user_id=1, title=title, position=i))
            for name in ["Навчання", "Робота", "Дім", "Особисте"]:
                db.add(models.Topic(user_id=1, name=name))
            db.add(models.Streak(user_id=1))
            db.commit()
    finally:
        db.close()


seed()

app = FastAPI(title="Memio API")
app.include_router(tasks.router)
app.include_router(days.router)
app.include_router(export.router)
app.mount("/uploads", StaticFiles(directory=days.UPLOADS_DIR), name="uploads")
app.mount("/exports", StaticFiles(directory=export.EXPORTS_DIR), name="exports")


@app.get("/")
def root():
    return {"message": "Memio працює"}
