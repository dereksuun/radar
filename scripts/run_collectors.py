from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.job_source import JobSource
from app.services.collectors.factory import build_collector
from app.services.jobs_repository import create_job_posting


def main() -> None:
    with SessionLocal() as db:
        stmt = (
            select(JobSource)
            .where(JobSource.is_active.is_(True))
            .order_by(JobSource.id.asc())
        )
        sources = db.scalars(stmt).all()

        if not sources:
            print("Nenhuma fonte ativa encontrada.")
            return

        for source in sources:
            print(f"\n=== Coletando da fonte: {source.name} ({source.source_type}) ===")

            try:
                collector = build_collector(source)
                jobs = collector.fetch_jobs()
            except Exception as exc:
                print(f"Erro ao coletar {source.name}: {exc}")
                continue

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
