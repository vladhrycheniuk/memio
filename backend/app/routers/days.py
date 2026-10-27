import time
from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas

router = APIRouter(tags=["days"])

USER_ID = 1
UPLOADS_DIR = Path(__file__).resolve().parents[3] / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)


def find_memory(db: Session, day: date):
    return (
        db.query(models.DailyMemory)
        .filter_by(user_id=USER_ID, memory_date=day)
        .first()
    )


def get_or_create(db: Session, day: date):
    mem = find_memory(db, day)
    if not mem:
        mem = models.DailyMemory(user_id=USER_ID, memory_date=day)
        db.add(mem)
        db.commit()
        db.refresh(mem)
    return mem


def remove_file(name: str | None):
    if name:
        (UPLOADS_DIR / Path(name).name).unlink(missing_ok=True)


@router.get("/days", response_model=list[schemas.DayOut])
def list_days(start: date, end: date, db: Session = Depends(get_db)):
    return (
        db.query(models.DailyMemory)
        .filter(
            models.DailyMemory.user_id == USER_ID,
            models.DailyMemory.memory_date >= start,
            models.DailyMemory.memory_date <= end,
        )
        .all()
    )


@router.get("/days/{day}", response_model=schemas.DayOut)
def get_day(day: date, db: Session = Depends(get_db)):
    mem = find_memory(db, day)
    if mem:
        return mem
    return schemas.DayOut(memory_date=day)


@router.put("/days/{day}", response_model=schemas.DayOut)
def update_day(day: date, data: schemas.DayUpdate, db: Session = Depends(get_db)):
    mem = get_or_create(db, day)
    for key, value in data.model_dump(exclude_unset=True).items():
        if key == "note" and value:
            value = value[:280]
        setattr(mem, key, value)
    db.commit()
    db.refresh(mem)
    return mem


@router.post("/days/{day}/photo", response_model=schemas.DayOut)
def upload_photo(day: date, file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        img = Image.open(file.file)
        img = ImageOps.exif_transpose(img)
        img.thumbnail((1600, 1600))
        img = img.convert("RGB")
    except (UnidentifiedImageError, OSError):
        raise HTTPException(400, "Не вдалося прочитати зображення")

    name = f"{day.isoformat()}_{int(time.time())}.jpg"
    img.save(UPLOADS_DIR / name, "JPEG", quality=88)

    mem = get_or_create(db, day)
    remove_file(mem.photo_path)
    mem.photo_path = name
    db.commit()
    db.refresh(mem)
    return mem


@router.delete("/days/{day}/photo", response_model=schemas.DayOut)
def delete_photo(day: date, db: Session = Depends(get_db)):
    mem = get_or_create(db, day)
    remove_file(mem.photo_path)
    mem.photo_path = None
    db.commit()
    db.refresh(mem)
    return mem