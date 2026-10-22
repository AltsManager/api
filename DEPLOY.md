# Deploying to Datum Cloud

This repo deploys to [Datum Cloud](https://datum.net) Compute. `api` is live
at **https://grain-noodle-m23qc.datumproxy.net** (health: `/health`, docs:
`/docs`, admin: `/admin`). `.github/workflows/deploy.yml` automates the same
`datumctl compute deploy` flow on every push to `main`, once its one-time
setup (below) is done.

## Status

- [x] Datum Cloud project `altsmanager` (org: Humans of the Internet /
  `joe-company-inc-3a1tyj`), Compute enabled
- [x] Postgres: Supabase (session pooler, port 5432 -- not the transaction
  pooler on 6543, which doesn't play well with SQLAlchemy's plain pool /
  alembic), schema migrated, decided over self-hosting since Datum Compute
  has no persistent disk
- [x] Document storage: Wasabi bucket `altsmanager-documents`
  (`https://s3.wasabisys.com`, `us-east-1`, versioned), same reasoning as
  Postgres
- [x] `altsmanager-api-secrets` Secret created (`DATABASE_URL`, `SECRET_KEY`,
  `STORAGE_BACKEND`, `S3_*`) via `datumctl apply -f` -- native `Secret`
  objects aren't reachable through the datum-mcp `resource` tool, only
  `datumctl`/the console
- [x] First manual deploy done and verified end-to-end (see "Gotchas" below
  for what it took to get there)
- [ ] Datum service account for CI, scoped to only the `altsmanager` project
  (manual deploys so far used a user session, not a service account)
- [ ] GitHub repo secrets/variables (list below) -- `deploy.yml` itself is
  still unexercised by actual CI

## Architecture

```
GitHub (push to main)
  -> build image, push to ghcr.io/altsmanager/api (must be a PUBLIC package --
     Datum Compute has no documented imagePullSecrets flag on `compute deploy`)
  -> datumctl compute deploy altsmanager-api --runtime-class=general-purpose --http-port=8000

Datum Compute workload "altsmanager-api" (general-purpose runtime class)
  -> DATABASE_URL secret -> Supabase Postgres (external, session pooler)
  -> S3_* secrets -> Wasabi bucket (external)
  -> public HTTPS hostname via --http-port (Datum-generated *.datumproxy.net;
     api.altsmanager.org not yet attached as a custom hostname)
```

Postgres and document storage are **not** Datum Compute workloads -- both need
persistent state Datum Compute's container runtime doesn't offer, so they're
external managed services the api workload connects to.

## Gotchas found getting this running (read before touching the Dockerfile/deploy flags)

1. **Runtime class must be `general-purpose`, not the platform-default
   `unikernel`.** `unikernel` (Unikraft) only runs specially-built
   position-independent binaries; a plain `docker build` image won't boot
   under it (manifests as `ImageUnavailable`-looking failures, not an obvious
   "wrong runtime" error). **Runtime class is immutable once a workload
   exists** -- getting it wrong means delete + recreate. Always pass
   `--runtime-class=general-purpose` explicitly.
2. **The container must bind to `::` (IPv6 wildcard), never `0.0.0.0`.**
   Datum Compute's network is IPv6-only -- an instance has no IPv4 address at
   all. Binding to `0.0.0.0` looks completely healthy in the app's own logs
   (and even in `compute_workload_diagnose`) while the ALB gets instant
   connection-refused on every request. The Dockerfile's `CMD` passes
   `--host ::` to uvicorn for this reason.
3. **Trust the edge's proxy headers**, or redirects break. Datum's edge
   terminates TLS and forwards plain HTTP to the container, but uvicorn
   doesn't know that by default, so it generates `Location: http://...`
   redirects -- which a browser correctly refuses to follow from an HTTPS
   page. Fixed with `--proxy-headers --forwarded-allow-ips='*'` (safe here:
   the container has no other public ingress path than Datum's edge).
4. **GHCR packages are private by default.** Datum Compute can't pull a
   private image anonymously, and `datumctl compute deploy` has no
   `imagePullSecrets`-equivalent flag. Make the package public: org ->
   Packages -> the package -> Package settings -> Change visibility.
5. **Prefer deploying by image digest** (`ghcr.io/owner/image@sha256:...`)
   over a mutable tag. A `datumctl compute deploy` re-run with the *same tag*
   did not reliably pick up a newly-pushed image during testing here; pinning
   the digest forced a correct pull every time.
6. **After a redeploy, give the edge real time to settle before concluding
   something is broken.** Even with everything else correct, the ALB
   reported `serving: true` / `confidence: unverified` while still returning
   503s with `UF` (upstream connection failure) response flags for over a
   minute after a clean rollout -- `alb_traffic_summary` and
   `compute_workload_diagnose` are the right tools to check (they'll show the
   app/workload as genuinely healthy while the edge path is still catching
   up), not a sign the deploy itself failed.

## One-time setup (remaining)

1. **Create a Datum service account** scoped to only the `altsmanager`
   project (see note in `deploy.yml` about datum-cloud/datumctl#324), download
   its credentials JSON, and set it as the `DATUM_SERVICE_ACCOUNT_KEY` GitHub
   Actions secret in this repo.
2. **Run the `Deploy` workflow** (push to `main`, or `workflow_dispatch`) and
   confirm it reaches the same state the manual deploys already did.

## Required GitHub secrets/variables

| Name | Type | Purpose |
|---|---|---|
| `DATUM_SERVICE_ACCOUNT_KEY` | secret | Service account credentials JSON for `datumctl login --credentials` |

(`GITHUB_TOKEN` for GHCR push is automatic, no setup needed.)
