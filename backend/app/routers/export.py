import calendar
from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..printing import PrintOptions, render_month

router = APIRouter(tags=["export"])

USER_ID = 1
ROOT = Path(__file__).resolve().parents[3]
UPLOADS_DIR = ROOT / "uploads"
EXPORTS_DIR = ROOT / "exports"
EXPORTS_DIR.mkdir(exist_ok=True)
LOGO_PATH = ROOT / "assets" / "logo.png"


def free_name(base: str, ext: str) -> Path:
    path = EXPORTS_DIR / f"{base}.{ext}"
    n = 2
    while path.exists():
        path = EXPORTS_DIR / f"{base}_{n}.{ext}"
        n += 1
    return path


@router.post("/print/month")
def print_month(data: schemas.PrintRequest, db: Session = Depends(get_db)):
    last = calendar.monthrange(data.year, data.month)[1]
    rows = (
        db.query(models.DailyMemory)
        .filter(
            models.DailyMemory.user_id == USER_ID,
            models.DailyMemory.memory_date >= date(data.year, data.month, 1),
            models.DailyMemory.memory_date <= date(data.year, data.month, last),
        )
        .all()
    )

    # у друк потрапляють лише фото; настрій (смайлики) і записки не беруться
    photos = {}
    for row in rows:
        if row.photo_path:
            path = UPLOADS_DIR / Path(row.photo_path).name
            if path.exists():
                photos[row.memory_date.day] = path

    opts = PrintOptions(
        frame_style=data.frame_style,
        frame_color=data.frame_color,
        frame_width=data.frame_width,
        corners=data.corners,
        orientation=data.orientation,
        show_logo=data.show_logo,
    )

    if data.preview:
        img = render_month(data.year, data.month, photos, opts, dpi=90, logo_path=LOGO_PATH)
        out = EXPORTS_DIR / "preview.png"
        img.save(out)
        return {"file": out.name, "path": str(out), "folder": str(EXPORTS_DIR)}

    img = render_month(data.year, data.month, photos, opts, dpi=300, logo_path=LOGO_PATH)
    out = free_name(f"memio_{data.year}-{data.month:02d}", data.format)
    if data.format == "pdf":
        img.save(out, "PDF", resolution=300.0)
    else:
        img.save(out, dpi=(300, 300))
    return {"file": out.name, "path": str(out), "folder": str(EXPORTS_DIR)}
