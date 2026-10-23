from fastapi import FastAPI
from .database import Base, engine
from . import models  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Memio API")


@app.get("/")
def root():
    return {"message": "Memio працює 🌊"}