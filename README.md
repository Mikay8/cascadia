# Cascadia

Cascadia is a multi-tenant web app for CDFIs (community development financial institutions). It tracks investor capital in ranked classes, ingests loan activity from a servicing provider, and calculates how repayments and losses are allocated across those classes each period.

Version 1 tracks and reports. It does not move money.

**Status:** early build. The repo skeleton is in place (increment 0.4). See [`docs/PLAN.md`](docs/PLAN.md) for what is done and what comes next.

## Stack

| Layer | Choice |
| --- | --- |
| Back end | Python 3.12, Django 5.2 LTS, Celery (from increment 3.2) |
| Database | PostgreSQL 18, one schema per tenant |
| Front end | React 19 with Vite, plain JavaScript |
| Hosting | Railway staging (production later), kept portable to AWS; see `docs/INFRASTRUCTURE.md` |

## Getting started

### Prerequisites

- Python 3.12
- Node 22
- Docker, to run the full stack with `docker compose up` (Postgres 18, Django, and Vite). Without Docker, run PostgreSQL 18 yourself for the back-end tests that use the database.

Copy [`.env.example`](.env.example) to `.env` and fill in local values. Never commit `.env` or any real credentials.

### Back end

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

python manage.py runserver       # http://localhost:8000/healthz
pytest                           # tests
ruff check . && ruff format .    # lint and format
```

By default the back end connects to `postgres://cascadia:cascadia@localhost:5432/cascadia`. Set `DATABASE_URL` to change this.

### Front end

```bash
cd frontend
npm install

npm run dev      # http://localhost:5173, proxies /api to the back end
npm test         # tests
npm run lint     # lint, including the no-hardcoded-colors rule
npm run build    # production build
```

## Repository layout

```
backend/          Django project
frontend/         React app, design tokens, and local lint rules
golden-cases/     real past runs as fixtures; they define correct engine output
docs/             build plan, decisions log, design handoff
.github/          CI workflow and pull request template
```

## How work is done

- Work follows [`docs/PLAN.md`](docs/PLAN.md), one increment at a time. Each increment is one branch and one pull request, titled `[ID] Name`, for example `[1.3] Core tables and seed data`.
- Check [`docs/DECISIONS.md`](docs/DECISIONS.md) before assuming anything about rounding, corrections, or approvals. Open decisions block specific increments.
- CI runs lint, tests, and build on every pull request. A human reviews and merges every pull request; nobody merges their own.
- [`CLAUDE.md`](CLAUDE.md) holds the hard rules and conventions. The most important: money is `Decimal` only and is never calculated in the front end, allocations sum exactly to the cent, tenants never mix, and history is append-only.
