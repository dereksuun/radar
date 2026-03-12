from fastapi import APIRouter
from sqlalchemy import text

from app.db.session import SessionLocal

router = APIRouter(tags=["health"])


@router.get("/health")
def healthcheck() -> dict:
    db_status = "ok"

    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
    except Exception as exc:
        db_status = f"error: {exc}"

    return {
        "status": "ok",
        "database": db_status,
    }
