from datetime import datetime

import httpx

from app.schemas.job_posting import JobPostingIngestion
from app.services.collectors.base import BaseCollector


class RecruiteeCollector(BaseCollector):
    def fetch_jobs(self) -> list[JobPostingIngestion]:
        company_slug = self.config.get("company_slug")
        if not company_slug:
            raise ValueError("config.company_slug é obrigatório para fonte recruitee.")

        company_name = self.config.get("company_name", self.source_name)
        api_url = f"https://{company_slug}.recruitee.com/api/offers/"

        with httpx.Client(
            timeout=30.0,
            headers={"Accept": "application/json"},
        ) as client:
            response = client.get(api_url)
            response.raise_for_status()
            payload = response.json()

        offers = payload.get("offers", [])
        jobs: list[JobPostingIngestion] = []

        for item in offers:
            url = self._extract_url(company_slug, item)
            if not url:
                continue

            jobs.append(
                JobPostingIngestion(
                    external_id=str(item.get("id")) if item.get("id") is not None else None,
                    title=(item.get("title") or item.get("name") or "").strip(),
                    company=company_name,
                    url=url,
                    location_raw=self._extract_location(item),
                    description_raw=self._extract_description(item),
                    published_at=self._extract_published_at(item),
                    raw_payload=item,
                )
            )

        return jobs

    @staticmethod
    def _extract_url(company_slug: str, item: dict) -> str | None:
        for field_name in ("careers_url", "url", "careersApplyUrl"):
            value = item.get(field_name)
            if value:
                return str(value)

        slug = item.get("slug") or item.get("offer_slug")
        if slug:
            return f"https://{company_slug}.recruitee.com/o/{slug}"

        return None

    @staticmethod
    def _extract_location(item: dict) -> str | None:
        location = item.get("location")
        if isinstance(location, dict):
            parts = [
                location.get("city"),
                location.get("state"),
                location.get("country"),
            ]
            parts = [str(part).strip() for part in parts if part]
            if parts:
                return ", ".join(parts)

        locations = item.get("locations")
        if isinstance(locations, list) and locations:
            names: list[str] = []

            for loc in locations:
                if isinstance(loc, dict):
                    parts = [
                        loc.get("city"),
                        loc.get("state"),
                        loc.get("country"),
                        loc.get("name"),
                    ]
                    built = ", ".join(str(part).strip() for part in parts if part)
                    if built:
                        names.append(built)
                elif isinstance(loc, str) and loc.strip():
                    names.append(loc.strip())

            if names:
                return " | ".join(dict.fromkeys(names))

        for field_name in ("city", "country", "country_name", "location_name"):
            value = item.get(field_name)
            if value:
                return str(value).strip()

        return None

    @staticmethod
    def _extract_description(item: dict) -> str | None:
        chunks = []

        for field_name in ("description", "description_plain", "requirements", "employment_description"):
            value = item.get(field_name)
            if isinstance(value, str) and value.strip():
                chunks.append(value.strip())

        if not chunks:
            return None

        return "\n\n".join(chunks)

    @staticmethod
    def _extract_published_at(item: dict) -> datetime | None:
        for field_name in ("published_at", "updated_at", "created_at", "opened_at"):
            value = item.get(field_name)
            if not value:
                continue

            if isinstance(value, str):
                try:
                    return datetime.fromisoformat(value.replace("Z", "+00:00"))
                except ValueError:
                    continue

        return None
