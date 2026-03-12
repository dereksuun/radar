from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.candidate_profile import CandidateProfile
from app.schemas.candidate_profile import (
    CandidateProfileCreate,
    CandidateProfileResponse,
    CandidateProfileUpdate,
)

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.post(
    "",
    response_model=CandidateProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_profile(
    payload: CandidateProfileCreate,
    db: Session = Depends(get_db),
) -> CandidateProfile:
    profile = CandidateProfile(**payload.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("", response_model=list[CandidateProfileResponse])
def list_profiles(db: Session = Depends(get_db)) -> list[CandidateProfile]:
    stmt = select(CandidateProfile).order_by(CandidateProfile.id.desc())
    profiles = db.scalars(stmt).all()
    return list(profiles)


@router.get("/active", response_model=CandidateProfileResponse)
def get_active_profile(db: Session = Depends(get_db)) -> CandidateProfile:
    stmt = (
        select(CandidateProfile)
        .where(CandidateProfile.is_active.is_(True))
        .order_by(CandidateProfile.id.desc())
    )
    profile = db.scalars(stmt).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum perfil ativo encontrado.",
        )

    return profile


@router.patch("/{profile_id}", response_model=CandidateProfileResponse)
def update_profile(
    profile_id: int,
    payload: CandidateProfileUpdate,
    db: Session = Depends(get_db),
) -> CandidateProfile:
    profile = db.get(CandidateProfile, profile_id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil não encontrado.",
        )

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile
