# FlowShelter

FlowShelter helps freelancers and people with irregular income understand their available money, plan for essential bills, and work towards savings goals. It brings income, expenses, financial commitments, and cash-flow forecasts together so users can make a clearer plan between payments.

## Technology stack

| Component | Technologies |
| --- | --- |
| Web client | React, TypeScript, Vite, Oxlint |
| Mobile / desktop client | Python, Flet, HTTPX |
| Backend API | Python, FastAPI, Pydantic, Uvicorn |
| Database | PostgreSQL, SQLAlchemy, Psycopg |
| Authentication | JWT, Argon2 password hashing |

## Project structure

```text
flow-shelter/
├── backend/
│   ├── app/
│   │   ├── api/          # Authentication and feature endpoints
│   │   ├── core/         # Settings and security
│   │   ├── db/           # Database connections and base model
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Request and response validation
│   │   └── services/     # Financial calculations and business logic
│   ├── docs/             # API integration guide
│   ├── create_tables.py
│   └── requirements.txt
├── mobile/
│   ├── src/              # Flet screens, API client, themes, translations
│   ├── tests/
│   └── pyproject.toml
└── web/
    ├── src/              # React components, screens, and API client
    └── package.json
```

## Getting started

### Prerequisites

- Python 3.10 or newer; use a version supported by the pinned backend dependencies.
- Node.js and npm compatible with the Vite version in [web/package.json](./web/package.json).
- A running PostgreSQL database and its connection string.
- [uv](https://docs.astral.sh/uv/) for the Flet app commands below.

Run the API first, then start either client in a separate terminal. The examples below use PowerShell and assume you start from the repository root.

### 1. Set up the backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create a `.env` file inside [backend/](./backend/) with your database credentials and a generated secret:

```dotenv
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/flow_shelter
JWT_SECRET_KEY=replace-with-a-generated-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
FORECAST_HORIZON_DAYS=30
```

Generate the secret with:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Create the `flow_shelter` database in PostgreSQL before continuing, or replace the example connection string with one for an existing database. The `postgresql+psycopg://` prefix explicitly selects the Psycopg driver installed by this project. Preserve any SSL options required by your database provider. Keep the environment file and real credentials out of version control.

Initialize the tables and start the API:

```powershell
python create_tables.py
uvicorn app.index:app --reload
```

- API: <http://127.0.0.1:8000>
- Interactive API documentation: <http://127.0.0.1:8000/docs>
- Health check: <http://127.0.0.1:8000/health>
- Database health check: <http://127.0.0.1:8000/health/database>

Table initialization creates missing tables; it does not migrate existing table definitions. Review schema changes before using an existing database.

### 2. Run the Flet app

In a new terminal, from the repository root:

```powershell
cd mobile
uv sync
uv run flet run
```

To run the same app in a browser:

```powershell
uv run flet run --web
```

The app connects to `http://127.0.0.1:8000` by default. To use another API address, set the variable before starting it:

```powershell
$env:FLOWSHELTER_API_URL = "http://192.168.1.10:8000"
uv run flet run
```

For a physical device, use an API address reachable from that device. To expose the development API on your local network, run `uvicorn app.index:app --reload --host 0.0.0.0` from the backend directory.

See the [Flet app README](./mobile/README.md) for platform build commands.

### 3. Run the React client

In a new terminal, from the repository root:

```powershell
cd web
npm ci
npm run dev
```

Open the address printed by Vite, normally <http://localhost:5173>.

The client also defaults to `http://127.0.0.1:8000`. To change it, create a `.env.local` file inside [web/](./web/):

```dotenv
VITE_API_URL=http://127.0.0.1:8000
```

Restart Vite after changing this value. The API currently allows browser requests from `http://localhost:5173` and `http://localhost:5174`; add other client origins to the CORS configuration in [backend/app/index.py](./backend/app/index.py) when needed.

## Configuration

| Variable | Used by | Default / requirement |
| --- | --- | --- |
| `DATABASE_URL` | Backend | Required PostgreSQL connection string |
| `JWT_SECRET_KEY` | Backend | Required signing secret |
| `JWT_ALGORITHM` | Backend | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Backend | `30` |
| `FORECAST_HORIZON_DAYS` | Backend | `30` |
| `FLOWSHELTER_API_URL` | Flet app | `http://127.0.0.1:8000` |
| `VITE_API_URL` | React client | `http://127.0.0.1:8000` |

## Development checks

Run the web checks from [web/](./web/):

```powershell
npm run lint
npm run build
```

To preview the production web build locally:

```powershell
npm run preview
```

Run the Flet app tests from [mobile/](./mobile/):

```powershell
uv run pytest
```
