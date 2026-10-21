# Deploying to Datum Cloud

This repo deploys to [Datum Cloud](https://datum.net) Compute via
`.github/workflows/deploy.yml`, which runs on every push to `main`. This
document is the one-time setup that workflow depends on, plus the pieces that
still need to be verified once Compute access is live (see status below).

## Status

- [x] Datum Cloud project `altsmanager` created (org: Humans of the Internet /
  `joe-company-inc-3a1tyj`)
- [ ] **Compute enabled for this project** — blocking everything below.
  Requested from Datum; nothing here can be applied or verified until it's
  granted.
- [ ] Postgres: a Supabase project for AltsManager (decided over self-hosting
  on Datum Compute, since Datum Compute has no persistent disk — a container
  restart would lose all data)
- [ ] Document storage: an S3-compatible bucket (e.g. Wasabi) — same reasoning
  as Postgres: `STORAGE_BACKEND=local` cannot be used here, only `s3`
- [ ] Datum service account for CI, scoped to only the `altsmanager` project
- [ ] GitHub repo secrets/variables (list below)

## Architecture

```
GitHub (push to main)
  -> build image, push to ghcr.io/altsmanager/api
  -> datumctl compute deploy altsmanager-api --http-port=8000

Datum Compute workload "altsmanager-api"
  -> DATABASE_URL secret -> Supabase Postgres (external)
  -> S3_* secrets -> Wasabi (or other S3-compatible) bucket (external)
  -> public HTTPS hostname via --http-port (Datum-generated, no custom domain yet)
```

Postgres and document storage are **not** Datum Compute workloads -- both need
persistent state Datum Compute's container runtime doesn't offer, so they're
external managed services the api workload connects to.

## One-time setup

1. **Get Compute enabled** for the `altsmanager` project in the Humans of the
   Internet org. (Nothing past this point can happen without it.)

2. **Create the Supabase project**, run migrations against it once
   (`alembic upgrade head` with `DATABASE_URL` pointed at it), and note its
   connection string.

3. **Create an S3-compatible bucket** (Wasabi or similar) for documents, and
   note its credentials.

4. **Create a Datum Secret** holding the app's runtime config -- `SECRET_KEY`
   (generate with `python -c "import secrets; print(secrets.token_urlsafe(48))"`),
   `DATABASE_URL`, `CORS_ORIGINS` (the web app's deployed URL), `STORAGE_BACKEND=s3`,
   and the `S3_*` values. This is created once via a Workload manifest apply
   (not via `datumctl compute deploy`, which has no documented way to attach
   secret references) and the Workload's `envFrom` references it.

5. **Create a Datum service account** scoped to only the `altsmanager`
   project (see note in `deploy.yml` about datum-cloud/datumctl#324), download
   its credentials JSON, and set it as the `DATUM_SERVICE_ACCOUNT_KEY` GitHub
   Actions secret in this repo.

6. **First deploy**: either push to `main`, or run the `Deploy` workflow
   manually (`workflow_dispatch`). This creates the `altsmanager-api` Compute
   workload and gives it a public HTTPS hostname -- note that hostname, it's
   needed by the `web` repo's `API_PUBLIC_URL` variable.

## Verify once Compute access is granted

The `deploy.yml` workflow was written against the Datum compute guide's
documented CLI shape, but untested against a real deployment (no access yet):

- Does `datumctl compute deploy <name> --image=... --http-port=...`, run
  again against an existing workload, preserve its `envFrom`/Secret
  references, or does it need those passed again on every call?
- The exact non-interactive `datumctl login --credentials` behavior
  (datum-cloud/datumctl#324 describes a failure mode when the service account
  can see more than one project/context).

## Required GitHub secrets/variables

| Name | Type | Purpose |
|---|---|---|
| `DATUM_SERVICE_ACCOUNT_KEY` | secret | Service account credentials JSON for `datumctl login --credentials` |

(`GITHUB_TOKEN` for GHCR push is automatic, no setup needed.)
