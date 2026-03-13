from datetime import datetime, timezone

import httpx

from app.schemas.job_posting import JobPostingIngestion
from app.services.collectors.base import BaseCollector


class LeverCollector(BaseCollector):
    def fetch_jobs(self) -> list[JobPostingIngestion]:
        site = self.config.get("site") or self.config.get("company_slug")
        if not site:
            raise ValueError("config.site ou config.company_slug é obrigatório para fonte lever.")

        api_base_url = self.config.get("api_base_url", "https://api.lever.co")
        company_name = self.config.get("company_name", self.source_name)
        limit = int(self.config.get("limit", 100))
        skip = 0

        jobs: list[JobPostingIngestion] = []

        with httpx.Client(
            timeout=30.0,
            headers={"Accept": "application/json"},
        ) as client:
            while True:
                response = client.get(
                    f"{api_base_url.rstrip('/')}/v0/postings/{site}",
                    params={
                        "mode": "json",
                        "limit": limit,
                        "skip": skip,
                    },
                )
                response.raise_for_status()
                payload = response.json()

                if not payload:
                    break

                for item in payload:
                    hosted_url = item.get("hostedUrl") or item.get("applyUrl")
                    if not hosted_url:
                        continue

                    categories = item.get("categories") or {}
                    description_raw = (
                        item.get("descriptionPlain")
                        or item.get("descriptionBodyPlain")
                        or item.get("description")
                        or item.get("descriptionBody")
                    )

                    jobs.append(
                        JobPostingIngestion(
                            external_id=item.get("id"),
                            title=(item.get("text") or "").strip(),
                            company=company_name,
                            url=hosted_url,
                            location_raw=self._extract_location(categories),
                            description_raw=description_raw,
                            published_at=self._extract_published_at(item),
                            raw_payload=item,
                        )
                    )

                if len(payload) < limit:
                    break

                skip += limit

        return jobs

    @staticmethod
    def _extract_location(categories: dict) -> str | None:
        if not categories:
            return None

        if categories.get("location"):
            return categories["location"]

        all_locations = categories.get("allLocations")
        if isinstance(all_locations, list) and all_locations:
            names = [str(loc).strip() for loc in all_locations if str(loc).strip()]
            return " | ".join(names) if names else None

        return None

    @staticmethod
    def _extract_published_at(item: dict) -> datetime | None:
        for field_name in ("createdAt", "updatedAt"):
            value = item.get(field_name)
            if value is None:
                continue

            if isinstance(value, (int, float)):
                return datetime.fromtimestamp(value / 1000, tz=timezone.utc)

            if isinstance(value, str):
                try:
                    return datetime.fromisoformat(value)
                except ValueError:
                    if value.isdigit():
                        return datetime.fromtimestamp(int(value) / 1000, tz=timezone.utc)

        return None
