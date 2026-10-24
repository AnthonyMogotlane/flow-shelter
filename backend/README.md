# Flow Shelter API

Backend API for Flow Shelter, built with FastAPI, SQLAlchemy, and PostgreSQL.

## Getting started

Run all commands from `backend/`.

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Environment variables

Create `backend/.env` (git-ignored, never commit it):

```dotenv
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DBNAME?sslmode=require
JWT_SECRET_KEY=<generate-with-the-command-below>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

- `DATABASE_URL` is your PostgreSQL connection string — copy it from your
  provider (Neon, Supabase, Railway) or use
  `postgresql://postgres:postgres@localhost:5432/flow_shelter` for local.
  It must start with `postgresql://`, not `postgres://`.
- Generate `JWT_SECRET_KEY` with
  `python -c "import secrets; print(secrets.token_urlsafe(48))"`.
- `JWT_ALGORITHM` and `ACCESS_TOKEN_EXPIRE_MINUTES` are optional and default to
  `HS256` and `30`.

When deploying, set the same four values in your host's environment settings.

### Create tables and run

```bash
python create_tables.py
uvicorn app.index:app --reload
```

API: <http://127.0.0.1:8000> · Docs: <http://127.0.0.1:8000/docs>

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/` | API name and slogan |
| GET | `/health` | Liveness check |
| GET | `/health/database` | Database check (`503` if unreachable) |
| GET | `/api/test/` | Test route |
| POST | `/auth/register` | Create a user (`201`; `409` if email taken) |
| POST | `/auth/login` | Get an access token (`401` invalid credentials) |
| GET | `/auth/me` | Current user |

Protected routes need `Authorization: Bearer <access_token>`.

### `POST /auth/register`

```json
{ "name": "Anthony", "email": "anthony@example.com", "password": "correct-horse-battery" }
```

Password must be 12–128 characters. Responds with the user:

```json
{ "id": 1, "name": "Anthony", "email": "anthony@example.com", "is_active": true }
```

### `POST /auth/login`

```json
{ "email": "anthony@example.com", "password": "correct-horse-battery" }
```

```json
{ "access_token": "eyJhbGciOiJIUzI1NiIs...", "token_type": "bearer" }
```

### `GET /auth/me`

```bash
curl http://127.0.0.1:8000/auth/me -H "Authorization: Bearer <TOKEN>"
```

Returns the current user. `401` for an invalid or expired token.

## Docs
