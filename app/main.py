from fastapi import FastAPI
from app.services import csv

app = FastAPI()


app.include_router(csv.router, prefix="/upload", tags=["upload"])


@app.get("/health")
async def health():
    return {"status": "ok"}
