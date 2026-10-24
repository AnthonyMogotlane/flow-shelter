#!/bin/sh
# Azure App Service startup command.
# The whole repository is deployed, but the FastAPI app lives in backend/,
# so move into it before starting uvicorn.
cd backend && exec uvicorn app.index:app --host 0.0.0.0 --port 8000
