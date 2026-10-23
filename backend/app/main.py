from fastapi import FastAPI
from app.api.endpoints import test

app = FastAPI()

app.include_router(
    test.router,
    prefix="/api/test",
    tags=["Test"]
)

@app.get("/")
def root():
    return {"name": "Flow Shelter", "slogan": "Plan for the days between paydays"}