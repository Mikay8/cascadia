# Back end

Django project. The root `CLAUDE.md` hard rules apply here first.

## Layout

```
config/settings/base.py        shared settings, no secrets
config/settings/dev.py         local development (default for manage.py)
config/settings/test.py        pytest (set in pyproject.toml)
config/settings/production.py  staging and production; requires every secret from the environment
config/urls.py                 routes; /healthz is the liveness check
tests/                         pytest suite
```

Apps go in their own top-level folders (for example `funds/`, `waterfall/`). Business logic lives in a `services.py` module per app, not in views or models. Calculation code is pure functions with no database access.

## Commands

Run from `backend/` with Python 3.12 and a virtual environment.

```
pip install -r requirements-dev.txt
pytest
ruff check . && ruff format .
python manage.py makemigrations --check --dry-run   # CI fails on missing migrations
```

Tests need PostgreSQL at `DATABASE_URL` (default `postgres://cascadia:cascadia@localhost:5432/cascadia`). SQLite is not supported, since schema-per-tenant needs Postgres.

## Conventions

- Type hints everywhere; ruff enforces them (`ANN`).
- Money is `Decimal` in Python and `NUMERIC` in the database, sent over the API as strings.
- Datetimes are timezone-aware (ruff `DTZ`).
- Every API write produces an audit entry (from increment 1.6).
