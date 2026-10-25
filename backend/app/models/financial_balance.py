from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class FinancialBalance(Base, TimestampMixin):
    """Money available now — onboarding step 2. One row per user."""

    __tablename__ = "financial_balances"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    available_balance: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    existing_savings: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
