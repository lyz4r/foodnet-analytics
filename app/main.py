from fastapi import FastAPI
from app.services import csv
from app.services.auth import auth
from app.services import chart_service
from app.database import utils
from app.services.auth.utils import limiter

app = FastAPI()
app.state.limiter = limiter


app.include_router(csv.router, prefix="/upload", tags=["upload"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(utils.router, prefix="/db", tags=["db"])
app.include_router(chart_service.router, prefix="/chart", tags=["chart"])


@app.get("/health")
async def health():
    return {"status": "ok"}
