# AltsManager API

AltsManager is an open-source, privacy-oriented, AI-forward platform for tracking
alternative investments — private stock, SAFE notes, real property, LLC interests,
private equity, VC fund LP positions, crypto, artwork, and more — across multiple
investing entities. It tracks transactions, ownership, documents (including K-1s
and other tax forms), and counterparties (lawyers, accountants, fund managers),
and is designed to be self-hosted so your data stays yours.

This repo is the backend API (FastAPI). It's early — currently just the core
ledger data model (entities, investments, ownership, transactions, documents).
CRUD endpoints, auth, document storage, integrations (e.g. Carta), and AI agents
for recurring data collection are on the roadmap.

## Requirements

- Python 3.12
- Docker (for local Postgres) — [Colima](https://github.com/abiosoft/colima) or
  Docker Desktop both work

## Setup

```bash
git clone https://github.com/AltsManager/api.git
cd api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

cp .env.example .env          # adjust if needed
docker compose up -d postgres
alembic upgrade head

uvicorn app.main:app --reload
```

Visit:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Health check: http://127.0.0.1:8000/health

## Development

```bash
ruff check .                              # lint
pytest                                    # run tests (needs postgres up)
alembic revision --autogenerate -m "..."  # generate a migration after model changes
alembic upgrade head                      # apply migrations
```

## Project structure

```
app/
  core/      settings, security, shared FastAPI dependencies
  db/        SQLAlchemy engine/session setup
  models/    SQLAlchemy ORM models (entity, investment, ownership, transaction, document, ...)
  schemas/   Pydantic request/response schemas
  crud/      data-access layer
  services/  storage backends and other integrations
  routers/   FastAPI route handlers
alembic/     database migrations
tests/       pytest suite
```
