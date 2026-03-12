from datetime import datetime

import httpx

from app.schemas.job_posting import JobPostingIngestion
from app.services.collectors.base import BaseCollector


class GreenhouseCollector(BaseCollector):
    def fetch_jobs(self) -> list[JobPostingIngestion]:
        company_slug = self.config.get("company_slug")
        if not company_slug:
            raise ValueError("config.company_slug é obrigatório para fonte greenhouse.")

        api_url = f"https://boards-api.greenhouse.io/v1/boards/{company_slug}/jobs"

        with httpx.Client(timeout=30.0) as client:
            response = client.get(api_url)
            response.raise_for_status()
            payload = response.json()

        jobs: list[JobPostingIngestion] = []

        for item in payload.get("jobs", []):
            absolute_url = item.get("absolute_url")
            if not absolute_url:
                continue

            updated_at = item.get("updated_at")
            published_at = None

            if updated_at:
                try:
                    published_at = datetime.fromisoformat(updated_at)
                except ValueError:
                    published_at = None

            location_name = None
            location_obj = item.get("location")
            if isinstance(location_obj, dict):
                location_name = location_obj.get("name")

            jobs.append(
                JobPostingIngestion(
                    external_id=str(item.get("id")) if item.get("id") is not None else None,
                    title=item.get("title", "").strip(),
                    company=self.source_name,
                    url=absolute_url,
                    location_raw=location_name,
                    description_raw=None,
                    published_at=published_at,
                    raw_payload=item,
                )
            )

        return jobs
