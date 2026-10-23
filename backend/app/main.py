from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"name": "Flow Shelter", "slogan": "Plan for the days between paydays"}