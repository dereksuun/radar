from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.profile import router as profile_router
from app.api.routes.sources import router as sources_router
from app.core.config import get_settings
from app.db.init_db import init_db


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(profile_router, prefix=settings.api_prefix)
app.include_router(sources_router, prefix=settings.api_prefix)


@app.get("/")
def root() -> dict:
    return {"message": f"{settings.app_name} is running"}
