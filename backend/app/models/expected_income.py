from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin

EXPECTED_INCOME_STATUSES = ("expected", "received", "cancelled")


class ExpectedIncome(Base, TimestampMixin):
    """Money the user expects to receive — onboarding step 3."""

    __tablename__ = "expected_incomes"
    __table_args__ = (
        CheckConstraint(
            "status IN ('expected', 'received', 'cancelled')",
            name="ck_expected_incomes_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source: Mapped[str] = mapped_column(String(150), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    expected_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="expected", server_default="expected"
    )
