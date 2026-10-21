# Security Policy

AltsManager is designed to be self-hosted and handles sensitive financial and
tax data (ownership records, transactions, K-1s and other tax documents). We
take security issues seriously and appreciate responsible disclosure.

## Reporting a vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.
Instead, report them privately using
[GitHub Security Advisories](https://github.com/AltsManager/api/security/advisories/new)
for this repository.

Include as much detail as you can:

- A description of the vulnerability and its potential impact
- Steps to reproduce (a minimal repro is ideal)
- Any relevant logs, screenshots, or proof-of-concept code

We'll acknowledge your report, investigate, and keep you updated as we work
toward a fix. Once a fix is released, we'll credit you (unless you'd prefer
otherwise) in the release notes.

## Supported versions

This project is pre-1.0 and under active development. Only the `main` branch
receives security fixes; there are no maintained release branches yet.

## Security model and known tradeoffs

This is a good-faith summary of the current design, intended to help
self-hosters make informed decisions — not a guarantee of fitness for any
particular threat model.

- **Single-tenant authorization.** Any authenticated user can read all
  entities, investments, transactions, and documents in the instance; write
  access is gated by role (`ADMIN`/`STAFF`), not by per-user data ownership.
  This matches the intended self-hosted, single-household/single-organization
  use case. If you add multiple unrelated users to one instance expecting
  per-user data isolation, that isolation does **not** currently exist.
- **No signup endpoint by design.** The first admin is bootstrapped via
  `scripts/create_admin.py`; additional users are created by an existing
  admin.
- **Sessions are stateless JWTs** in an httpOnly, `SameSite=Lax` cookie with a
  short default expiry (60 minutes). There is no server-side revocation list,
  so a stolen token remains valid until it expires or the `SECRET_KEY` is
  rotated.
- **`SECRET_KEY` must be a unique, random value in production** — the app
  refuses to start with the placeholder default when `ENVIRONMENT=production`.
  Rotating it invalidates all existing sessions.
- **Login attempts are rate-limited per-process**, not across a multi-worker
  or multi-instance deployment. If you run several API workers behind a load
  balancer, consider pairing this with rate limiting at the edge (reverse
  proxy/WAF).
