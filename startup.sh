#!/bin/sh
# Azure App Service startup command.
# "Flatten backend to repo root" in the deploy workflow copies backend/ to the
# wwwroot root, so the app package and .env-ed requirements sit at the top level.
# App Service puts Oryx's antenv site-packages on PYTHONPATH and calls this file
# from the repo root, so uvicorn resolves from there.
exec python -m uvicorn app.index:app --host 0.0.0.0 --port 8000
