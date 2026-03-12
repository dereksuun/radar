from app.db.base import Base
from app.db.session import engine

# Importa os models para registrar no metadata
from app.models import CandidateProfile, JobPosting, JobSource  # noqa: F401


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
