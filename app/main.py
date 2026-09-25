from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import init_db
from app.routes import router

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="FitBuddy - AI Fitness Plan Generator",
    description="AI-powered 7-day fitness planning application using FastAPI, SQLite, SQLAlchemy and Gemini.",
    version="1.0.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=PROJECT_DIR / "static"), name="static")
templates = Jinja2Templates(directory=PROJECT_DIR / "templates")

app.include_router(router)
