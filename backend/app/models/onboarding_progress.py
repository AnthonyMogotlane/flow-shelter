from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class OnboardingProgress(Base, TimestampMixin):
    """Resumable onboarding state — one row per user."""

    __tablename__ = "onboarding_progress"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    current_step: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default="1"
    )
    is_complete: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
