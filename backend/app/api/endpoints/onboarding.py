from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.onboarding import (
    OnboardingDraft,
    OnboardingPatch,
    OnboardingStepUpdate,
)
from app.services import onboarding_service as service

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


@router.get("", response_model=OnboardingDraft)
def get_onboarding(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the saved draft and the current step so onboarding can resume."""
    return service.get_draft(db, current_user.id)


@router.patch("", response_model=OnboardingDraft)
def save_onboarding(
    patch: OnboardingPatch,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Save partial progress. Omitted sections are left untouched; collections
    that are sent replace the existing ones."""
    service.save_draft(db, current_user.id, patch)
    return service.get_draft(db, current_user.id)


@router.put("/step", response_model=OnboardingDraft)
def update_step(
    body: OnboardingStepUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Record which step the user is on (1-5) for resumable onboarding."""
    service.update_step(db, current_user.id, body.current_step)
    return service.get_draft(db, current_user.id)


@router.post("/complete", response_model=OnboardingDraft)
def complete_onboarding(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Validate the minimum data set and finalise onboarding."""
    try:
        service.complete(db, current_user.id)
    except service.OnboardingIncompleteError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={"message": "Onboarding is incomplete", "missing": exc.missing},
        )
    return service.get_draft(db, current_user.id)
