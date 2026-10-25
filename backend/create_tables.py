
from app.db.base import Base
from app.db.session import engine

# Import every model so it is registered on Base.metadata before create_all.
from app.models.user import User
from app.models.financial_profile import FinancialProfile
from app.models.financial_balance import FinancialBalance
from app.models.expected_income import ExpectedIncome
from app.models.savings_goal import SavingsGoal
from app.models.financial_commitment import FinancialCommitment
from app.models.onboarding_progress import OnboardingProgress

Base.metadata.create_all(bind=engine)

# with engine.begin() as connection:
#     connection.execute(
#         text(
#             "DROP TABLE IF EXISTS users"
#         )
#     )

print("Database tables and schema updated successfully")
