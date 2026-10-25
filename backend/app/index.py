from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.api.endpoints import test

from app.db.session import get_db

from app.api.auth import router as auth_router
from app.api.v1.router import router as v1_router

app = FastAPI()

app.include_router(auth_router)

app.include_router(
    v1_router,
    prefix="/api",
)

app.include_router(
    test.router,
    prefix="/api/test",
    tags=["Test"]
)

@app.get("/")
def root():
    return {"name": "Flow Shelter", "slogan": "Plan for the days between paydays"}

@app.get("/health/database")
def check_database(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "connected",
            "database": "PostgreSQL"
        }
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable"
        )
        


@app.get("/health")
def health():
    return {"status": "healthy"}
