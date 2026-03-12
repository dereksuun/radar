from datetime import datetime

from pydantic import BaseModel, ConfigDict


class JobSourceBase(BaseModel):
    name: str
    source_type: str
    base_url: str
    config: dict | None = None


class JobSourceCreate(JobSourceBase):
    pass


class JobSourceUpdate(BaseModel):
    name: str | None = None
    source_type: str | None = None
    base_url: str | None = None
    config: dict | None = None
    is_active: bool | None = None


class JobSourceResponse(JobSourceBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
