from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CandidateProfileBase(BaseModel):
    name: str
    seniority: str | None = None
    location: str | None = None
    work_model: str | None = None
    min_salary: Decimal | None = None

    languages: str | None = None
    primary_skills: str | None = None
    secondary_skills: str | None = None
    strong_keywords: str | None = None
    elimination_keywords: str | None = None


class CandidateProfileCreate(CandidateProfileBase):
    pass


class CandidateProfileUpdate(BaseModel):
    name: str | None = None
    seniority: str | None = None
    location: str | None = None
    work_model: str | None = None
    min_salary: Decimal | None = None

    languages: str | None = None
    primary_skills: str | None = None
    secondary_skills: str | None = None
    strong_keywords: str | None = None
    elimination_keywords: str | None = None

    is_active: bool | None = None


class CandidateProfileResponse(CandidateProfileBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
