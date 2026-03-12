from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job_posting import JobPosting
from app.models.job_source import JobSource
from app.schemas.job_posting import JobPostingIngestion
from app.services.hash_service import generate_job_hash


def get_source_by_id(db: Session, source_id: int) -> JobSource | None:
    return db.get(JobSource, source_id)


def get_existing_job_by_hash(db: Session, job_hash: str) -> JobPosting | None:
    stmt = select(JobPosting).where(JobPosting.job_hash == job_hash)
    return db.scalars(stmt).first()


def create_job_posting(
    db: Session,
    *,
    source: JobSource,
    job_data: JobPostingIngestion,
) -> tuple[JobPosting, bool]:
    job_hash = generate_job_hash(
        source_type=source.source_type,
        external_id=job_data.external_id,
        title=job_data.title,
        company=job_data.company,
        url=str(job_data.url),
    )

    existing = get_existing_job_by_hash(db, job_hash)
    if existing:
        return existing, False

    job = JobPosting(
        source_id=source.id,
        external_id=job_data.external_id,
        job_hash=job_hash,
        title=job_data.title,
        company=job_data.company,
        url=str(job_data.url),
        location_raw=job_data.location_raw,
        description_raw=job_data.description_raw,
        published_at=job_data.published_at,
        raw_payload=job_data.raw_payload,
    )

    db.add(job)
    db.commit()
    db.refresh(job)
    return job, True
