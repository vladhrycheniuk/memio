import sys
import time
import threading
from pathlib import Path

import requests
import uvicorn
import flet as ft

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "frontend"))


def start_backend():
    config = uvicorn.Config("app.main:app", host="127.0.0.1", port=8000, log_level="warning")
    uvicorn.Server(config).run()


threading.Thread(target=start_backend, daemon=True).start()

for _ in range(50):
    try:
        requests.get("http://127.0.0.1:8000/")
        break
    except requests.ConnectionError:
        time.sleep(0.2)

from ui import main  # noqa: E402

if hasattr(ft, "run"):
    ft.run(main)
else:
    ft.app(target=main)