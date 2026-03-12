from datetime import datetime

from pydantic import BaseModel, HttpUrl


class JobPostingIngestion(BaseModel):
    external_id: str | None = None
    title: str
    company: str
    url: HttpUrl
    location_raw: str | None = None
    description_raw: str | None = None
    published_at: datetime | None = None
    raw_payload: dict | None = None
