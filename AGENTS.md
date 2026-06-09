# AGENTS.md

## Project overview

LexiScan-PAES is a Chilean PAES reading comprehension study platform. Full-stack: FastAPI (Python 3.12) backend + Ionic/Angular (Angular 20, Ionic 8) mobile-hybrid frontend. AI-powered question generation via Groq (Llama 3).

## Structure

All application code lives under `Producto/`. The root `package-lock.json` is a stale artifact — ignore it.

```
Producto/
├── docker-compose.yml          # PostgreSQL 15 container
├── lexiscan_schema.sql         # Auto-loaded at container init
├── datos_presentacion.sql      # Seed data for demos
├── backend/                    # FastAPI API
│   ├── main.py                 # Entry point
│   ├── database.py             # SQLAlchemy engine + session
│   ├── models.py               # ORM models
│   ├── crud.py                 # DB operations
│   ├── schemas.py              # Pydantic schemas
│   ├── services/               # Business logic (recomendaciones, impulsividad)
│   ├── scripts/                # Destructive migration/seed scripts
│   ├── tests/                  # Standalone integration tests
│   └── .env                    # Secrets — DO NOT COMMIT
└── LexiScan_Angular/lexi-scan/ # Frontend
    └── src/
```

## Running locally

### Database (Docker)

```bash
cd Producto
docker-compose up -d
```

Container name: `lexiscan_db_container`. Port: `5432`. Schema auto-runs on first `docker-compose up`.

### Backend

```bash
cd Producto/backend
python -m venv venv           # Must be Python 3.12.x
venv\Scripts\activate         # Windows
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd Producto/LexiScan_Angular/lexi-scan
npm install
ionic serve                   # Dev server on :4200
```

## Tests

Backend tests are standalone HTTP integration tests, not pytest fixtures. They call a running server on port 8001:

```bash
cd Producto/backend
python tests/test_api.py      # Requires server on :8001
```

Frontend: `ng test` (Karma/Jasmine). Lint: `ng lint`.

## Gotchas

- **Python version**: Must be 3.12.x. Python 3.15 breaks binary deps (psycopg2-binary, bcrypt).
- **Schema auto-init**: `docker-compose up` runs `lexiscan_schema.sql` only on first volume creation. Use `docker-compose down -v` to force re-init (destroys data).
- **`.env` contains real secrets** (`Producto/backend/.env`). Never commit this file. It has a GROQ_API_KEY already set.
- **`scripts/migrate_and_seed.py` is destructive** — drops tables and recreates them. Only run intentionally.
- **CORS**: Only `localhost:4200` and `localhost:8100` are allowed origins.
- **`textos_restantes`**: User's remaining texts counter decrements on each AI question generation. If users run out of texts, the API returns 403.
- **Passwords**: Stored as bcrypt hashes (not plaintext despite what README claims).
- **Skills enum**: `Localizar`, `Interpretar`, `Evaluar`, `Lectura_Critica`, `Vocabulario`, `Tipos_de_Texto`. DB names use underscores; API uses spaces.
- **Angular version**: This is Angular 20 + Ionic 8. Not the older Angular 15/16 patterns. Components use `standalone: true` and `@ionic/angular-toolkit` schematics.
- **Frontend styles**: SCSS (configured in `angular.json`). Not CSS.
- **Capacitor**: Mobile builds via `ionic capacitor build android`. Not Cordova.
- **DB defaults**: `database.py` constructs connection from `POSTGRES_*` env vars with hardcoded fallbacks (`user_lexiscan`, `password123`, `lexiscan_db`, `localhost:5432`). Override via env or `DATABASE_URL`.
- **Frontend API URL**: `src/environments/environment.ts` points to `http://localhost:8000`. Change for production.
- **Root `package-lock.json`**: Stale file at repo root. All Node work is in `Producto/LexiScan_Angular/lexi-scan/`.
