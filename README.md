# AltsManager API

AltsManager is an open-source, privacy-oriented, AI-forward platform for tracking
alternative investments — private stock, SAFE notes, real property, LLC interests,
private equity, VC fund LP positions, crypto, artwork, and more — across multiple
investing entities. It tracks transactions, ownership, documents (including K-1s
and other tax forms), and counterparties (lawyers, accountants, fund managers),
and is designed to be self-hosted so your data stays yours.

This repo is the backend API (FastAPI). It's early — currently the core ledger
data model, auth and CRUD for entities, counterparties, investments, ownership,
and transactions, document upload/download/review-status tracking, and a basic
admin UI for browsing data. Third-party integrations (e.g. Carta) and AI agents
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

# there's no signup endpoint by design — bootstrap the first admin user:
python -m scripts.create_admin --email you@example.com --name "Your Name" --password "change-me"

uvicorn app.main:app --reload
```

Visit:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Health check: http://127.0.0.1:8000/health
- Admin panel: http://127.0.0.1:8000/admin (log in with the admin user above — a basic
  auto-generated CRUD/browse UI over the database, not the real product UI, just
  useful for seeing data while the API and frontend are built out)

## Documents

Files are stored via a pluggable backend, set with `STORAGE_BACKEND` in `.env`:
- `local` (default) — kept on disk under `DOCUMENT_STORAGE_PATH`, nothing leaves
  the machine. Good fit for the "privacy-oriented" / self-hosted goal.
- `s3` — any S3-compatible object store (AWS S3, MinIO, Backblaze B2, ...),
  configured via the `S3_*` settings in `.env.example`.

Document *metadata* (filename, type, tax year, review status, links to the
entity/investment/transaction it belongs to) always lives in Postgres regardless
of backend. Upload via `POST /api/v1/documents` (or the nested
`/api/v1/entities/{id}/documents` / `/api/v1/investments/{id}/documents`), and
download via `GET /api/v1/documents/{id}/download`.

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
  services/  document storage backends (local disk / S3-compatible) and other integrations
  routers/   FastAPI route handlers
alembic/     database migrations
tests/       pytest suite
```
