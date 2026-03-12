from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    seniority: Mapped[str | None] = mapped_column(String(50), nullable=True)
    location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    work_model: Mapped[str | None] = mapped_column(String(50), nullable=True)
    min_salary: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)

    languages: Mapped[str | None] = mapped_column(Text, nullable=True)
    primary_skills: Mapped[str | None] = mapped_column(Text, nullable=True)
    secondary_skills: Mapped[str | None] = mapped_column(Text, nullable=True)
    strong_keywords: Mapped[str | None] = mapped_column(Text, nullable=True)
    elimination_keywords: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
