from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.job_source import JobSource
from app.services.collectors.greenhouse import GreenhouseCollector
from app.services.jobs_repository import create_job_posting


def main() -> None:
    with SessionLocal() as db:
        stmt = (
            select(JobSource)
            .where(JobSource.source_type == "greenhouse")
            .where(JobSource.is_active.is_(True))
            .order_by(JobSource.id.asc())
        )
        sources = db.scalars(stmt).all()

        if not sources:
            print("Nenhuma fonte greenhouse ativa encontrada.")
            return

        for source in sources:
            print(f"\nColetando vagas da fonte: {source.name}")

            collector = GreenhouseCollector(
                source_name=source.name,
                base_url=source.base_url,
                config=source.config,
            )

            jobs = collector.fetch_jobs()
            print(f"Vagas encontradas: {len(jobs)}")

            created_count = 0
            skipped_count = 0

            for job_data in jobs:
                _, created = create_job_posting(
                    db,
                    source=source,
                    job_data=job_data,
                )
                if created:
                    created_count += 1
                else:
                    skipped_count += 1

            print(f"Novas salvas: {created_count}")
            print(f"Duplicadas ignoradas: {skipped_count}")


if __name__ == "__main__":
    main()
