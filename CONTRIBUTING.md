# Contributing to AltsManager (API)

Thanks for your interest in contributing. This project is early and the data
model/API surface is still changing, so it's worth opening an issue to
discuss larger changes before investing time in a PR.

## Getting set up

Follow the [Setup section of the README](README.md#setup). In short:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
docker compose up -d postgres
alembic upgrade head
```

## Before opening a PR

```bash
ruff check .       # lint
pytest             # tests (needs postgres up)
```

If you changed any SQLAlchemy models, generate a migration:

```bash
alembic revision --autogenerate -m "describe the change"
```

## Pull requests

- Keep PRs focused — one logical change per PR is easier to review.
- Add or update tests for behavior you change.
- Use the PR template; link the issue it addresses if there is one.
- Security-sensitive changes (auth, access control, document storage) get
  extra scrutiny — see [SECURITY.md](SECURITY.md) for the project's security
  model.

## Reporting bugs / proposing features

Use the issue templates under `.github/ISSUE_TEMPLATE/`. For security
vulnerabilities, see [SECURITY.md](SECURITY.md) instead of opening a public
issue.

## Code of conduct

This project follows the [Code of Conduct](CODE_OF_CONDUCT.md). By
participating, you're expected to uphold it.
