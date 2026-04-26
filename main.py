from fastapi import FastAPI
from contextlib import asynccontextmanager

from core.database import create_db_and_tables
from api.routers import notes

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title="MedVigil API", lifespan=lifespan)

app.include_router(notes.router)
