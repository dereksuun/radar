from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.core.config import get_settings


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

app.include_router(health_router)


@app.get("/")
def root() -> dict:
    return {"message": f"{settings.app_name} is running"}
