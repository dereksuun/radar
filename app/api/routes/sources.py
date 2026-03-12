from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.job_source import JobSource
from app.schemas.job_source import JobSourceCreate, JobSourceResponse, JobSourceUpdate

router = APIRouter(prefix="/sources", tags=["sources"])


@router.post(
    "",
    response_model=JobSourceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_source(
    payload: JobSourceCreate,
    db: Session = Depends(get_db),
) -> JobSource:
    existing = db.scalars(
        select(JobSource).where(JobSource.name == payload.name)
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma fonte com esse nome.",
        )

    source = JobSource(**payload.model_dump())
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


@router.get("", response_model=list[JobSourceResponse])
def list_sources(db: Session = Depends(get_db)) -> list[JobSource]:
    stmt = select(JobSource).order_by(JobSource.id.desc())
    sources = db.scalars(stmt).all()
    return list(sources)


@router.patch("/{source_id}", response_model=JobSourceResponse)
def update_source(
    source_id: int,
    payload: JobSourceUpdate,
    db: Session = Depends(get_db),
) -> JobSource:
    source = db.get(JobSource, source_id)

    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fonte não encontrada.",
        )

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(source, field, value)

    db.commit()
    db.refresh(source)
    return source
