from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes_auth, routes_dashboard, routes_projects, routes_tasks, routes_users
from app.core.config import get_settings
from app.db.base import Base
from app.db.seed import seed
from app.db.session import SessionLocal, engine

# Register models on Base.metadata before create_all.
from app import models  # noqa: F401

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_auth.router)
app.include_router(routes_projects.router)
app.include_router(routes_tasks.router)
app.include_router(routes_dashboard.router)
app.include_router(routes_users.router)


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok", "app": settings.app_name}
