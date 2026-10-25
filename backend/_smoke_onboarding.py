"""Throwaway smoke test: exercises the onboarding + dashboard API against an
in-memory SQLite DB so nothing touches the real database."""

import os
import tempfile
from decimal import Decimal

# Must be set before app.core.config is imported.
_tmp = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp}/smoke.db"
os.environ["JWT_SECRET_KEY"] = "smoke-test-key"

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.db.base import Base  # noqa: E402
from app.db.session import get_db  # noqa: E402
import app.models.user  # noqa: E402,F401
import app.models.financial_profile  # noqa: E402,F401
import app.models.financial_balance  # noqa: E402,F401
import app.models.expected_income  # noqa: E402,F401
import app.models.savings_goal  # noqa: E402,F401
import app.models.financial_commitment  # noqa: E402,F401
import app.models.onboarding_progress  # noqa: E402,F401
from app.index import app  # noqa: E402

engine = create_engine(
    os.environ["DATABASE_URL"], connect_args={"check_same_thread": False}
)
TestSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

BASE = "/api/v1/endpoints"


def check(label, condition, detail=""):
    print(("PASS " if condition else "FAIL ") + label + (f"  {detail}" if not condition else ""))
    assert condition, label


# --- auth ---------------------------------------------------------------
r = client.post("/auth/register", json={"name": "Thandi Dlamini", "email": "t@x.com", "password": "correct-horse-battery"})
check("register 201", r.status_code == 201, r.text)
token = client.post("/auth/login", json={"email": "t@x.com", "password": "correct-horse-battery"}).json()["access_token"]
H = {"Authorization": f"Bearer {token}"}

check("onboarding requires auth", client.get(f"{BASE}/onboarding").status_code == 403)
check("dashboard requires auth", client.get(f"{BASE}/dashboard/overview").status_code == 403)

# --- draft --------------------------------------------------------------
r = client.get(f"{BASE}/onboarding", headers=H)
check("GET draft defaults", r.status_code == 200 and r.json()["current_step"] == 1 and r.json()["is_complete"] is False, r.text)

r = client.put(f"{BASE}/onboarding/step", json={"current_step": 3}, headers=H)
check("PUT step", r.status_code == 200 and r.json()["current_step"] == 3, r.text)
check("step validation 422", client.put(f"{BASE}/onboarding/step", json={"current_step": 9}, headers=H).status_code == 422)

r = client.post(f"{BASE}/onboarding/complete", headers=H)
check("complete too early -> 422 with missing", r.status_code == 422 and "available_balance" in r.text, r.text)

patch = {
    "financial_profile": {"work_type": "Graphic designer", "income_pattern": "irregular", "currency": "ZAR"},
    "financial_balance": {"available_balance": "18450.00", "existing_savings": "0.00"},
    "expected_incomes": [{"source": "Mokoena Studio project", "amount": "12000.00", "expected_date": "2026-11-05"}],
    "savings_goals": [{"name": "Emergency buffer", "target_amount": "30000.00", "saved_amount": "4500.00", "priority": "medium"}],
}
r = client.patch(f"{BASE}/onboarding", json=patch, headers=H)
body = r.json()
check("PATCH draft", r.status_code == 200, r.text)
check("draft echoes profile", body["financial_profile"]["currency"] == "ZAR", body)
check("draft money as string", body["financial_balance"]["available_balance"] == "18450.00", body)
check("draft has one income", len(body["expected_incomes"]) == 1, body)
check("draft has one goal", len(body["savings_goals"]) == 1, body)

# Retry the same PATCH: collections must not duplicate.
client.patch(f"{BASE}/onboarding", json=patch, headers=H)
body = client.get(f"{BASE}/onboarding", headers=H).json()
check("retry does not duplicate", len(body["expected_incomes"]) == 1 and len(body["savings_goals"]) == 1, body)

# Partial PATCH leaves other sections untouched.
client.patch(f"{BASE}/onboarding", json={"financial_balance": {"available_balance": "19000.00"}}, headers=H)
body = client.get(f"{BASE}/onboarding", headers=H).json()
check("partial patch keeps profile", body["financial_profile"]["work_type"] == "Graphic designer", body)
check("partial patch updates balance", body["financial_balance"]["available_balance"] == "19000.00", body)

# --- dashboard ----------------------------------------------------------
r = client.get(f"{BASE}/dashboard/overview", headers=H)
d = r.json()
check("overview 200", r.status_code == 200, r.text)
check("available_now", d["available_now"] == "19000.00", d)
check("next payment", d["next_expected_payment"]["source"] == "Mokoena Studio project", d)
check("goal progress 15%", d["savings_goals"][0]["progress_percentage"] == 15, d)
check("projected = available + income - commitments", d["projected_balance"] == "31000.00", d)
check("forecast flagged estimate", d["forecast_is_estimate"] is True, d)
check("payment_expected alert", any(a["type"] == "payment_expected" for a in d["alerts"]), d["alerts"])

r = client.get(f"{BASE}/dashboard/alerts", headers=H)
check("alerts endpoint", r.status_code == 200 and isinstance(r.json(), list), r.text)

# --- commitments affect the projection ----------------------------------
from datetime import date, timedelta  # noqa: E402

from app.models.financial_commitment import FinancialCommitment  # noqa: E402
from app.models.user import User as UserModel  # noqa: E402

_today = date.today()
with TestSession() as s:
    uid = s.query(UserModel).filter_by(email="t@x.com").one().id
    s.add_all([
        FinancialCommitment(user_id=uid, name="Rent", amount=7900, due_date=_today + timedelta(days=5)),
        FinancialCommitment(user_id=uid, name="Old bill", amount=999, due_date=_today + timedelta(days=5), is_paid=True),
        FinancialCommitment(user_id=uid, name="Far future", amount=500, due_date=_today + timedelta(days=90)),
    ])
    s.commit()

d = client.get(f"{BASE}/dashboard/overview", headers=H).json()
check("commitments only unpaid + in horizon", d["essential_commitments"] == "7900.00", d)
check("projected subtracts commitments", d["projected_balance"] == "19000.00" + Decimal("12000.00") - Decimal("7900.00") and d["projected_balance"] == "23100.00", d)

r = client.post(f"{BASE}/onboarding/complete", headers=H)
check("complete succeeds", r.status_code == 200 and r.json()["is_complete"] is True, r.text)

# --- ownership isolation ------------------------------------------------
client.post("/auth/register", json={"name": "Other User", "email": "o@x.com", "password": "correct-horse-battery"})
other = client.post("/auth/login", json={"email": "o@x.com", "password": "correct-horse-battery"}).json()["access_token"]
d2 = client.get(f"{BASE}/dashboard/overview", headers={"Authorization": f"Bearer {other}"}).json()
check("other user sees own empty data", d2["available_now"] == "0.00" and d2["next_expected_payment"] is None, d2)

print("\nALL CHECKS PASSED")
