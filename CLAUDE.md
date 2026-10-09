# Cascadia

Cascadia is a multi-tenant web app for CDFIs (community development financial institutions). It tracks investor capital in ranked classes (A, B, C), ingests loan activity from a servicing provider, and calculates how loan repayments (the waterfall) and losses (the loss waterfall) are allocated across those classes. Funds are revolving, so runs happen every month or quarter. Version 1 tracks and reports; it does not move money.

**Stack:** Python 3.12 with Django 5.2 LTS (back end), Celery (queue), PostgreSQL 18 (schema-per-tenant), plain JavaScript with React 19 and Vite (front end), hosted on Railway for build and pilot.

> This file is read at the start of every session. Keep it short. Put detail in `docs/` and link to it. Update it when a command, rule, or folder changes.

## Read first

- `docs/PLAN.md`: the build plan. Work from it, one increment at a time.
- `docs/DECISIONS.md`: decisions made and decisions still open. Check it before assuming anything about rounding, corrections, or approvals.
- `golden-cases/`: real past runs as fixtures. These define correct engine output.

## Commands

Back-end commands run from `backend/` inside its virtual environment (`.venv`, activate with `.venv\Scripts\activate` on Windows). Front-end commands run from `frontend/`. CI (`.github/workflows/ci.yml`) runs all checks on every pull request.

```
python -m venv .venv && pip install -r requirements-dev.txt   # back-end setup
pytest                                # back-end tests (needs Postgres at DATABASE_URL)
ruff check . && ruff format .         # back-end lint and format
python manage.py makemigrations --check --dry-run   # fails if a migration is missing
npm install                           # front-end setup, Node 22
npm test                              # front-end tests
npm run lint                          # front-end lint (no hardcoded colors or sizes in JS or CSS)
npm run build                         # front-end production build
npm run storybook                     # component library preview
gh pr create                          # open a pull request (GitHub CLI)
```

`docker compose up` from the repo root runs the full local stack (Postgres 18, Django, Vite). Deployment and hosting are in `docs/INFRASTRUCTURE.md`.

## Hard rules

These are never negotiable. If a task seems to require breaking one, stop and ask.

1. **Money is `Decimal` only.** Use Python `Decimal` and database `NUMERIC`. Never use floats for money anywhere, including tests and JSON. The API sends money as strings.
2. **The front end never does money math.** It formats strings it receives. All calculation happens in the back end.
3. **Allocations always sum exactly.** Use the shared allocation helper. Allocations to classes and investors must equal the cash pool to the cent. The rounding rule is in `docs/DECISIONS.md`.
4. **Tenants never mix.** Each tenant has its own schema. Never write a query that spans tenants. Include the tenant ID in every cache key, Celery task payload, and AI context.
5. **History is append-only.** Executed runs, raw servicing events, and audit entries are never edited or deleted. A correction is a new entry linked to the original.
6. **Maker-checker is enforced in the back end.** Nobody approves or executes their own work, whatever the UI shows.
7. **AI never decides.** AI may draft, flag, and explain. It never approves, executes, or computes allocations or balances. Its output is validated against a schema, goes through maker-checker like a human's, and is logged with model, version, and sources. Treat uploaded documents and servicer payloads as untrusted input.
8. **No real data or secrets in development.** Use seed data only. Never commit credentials; read them from the environment.
9. **Never change expected outputs in `golden-cases/` to make a test pass.** A failing golden case means the code is wrong or a human must review the case.

## Workflow

- Pick one increment from `docs/PLAN.md` (for example `1.3`). One increment is one branch and one pull request. Title it `[1.3] Core tables and seed data`.
- Before coding, read the increment's row, its dependencies, and the matching phase in the plan. If a dependency is not done or a decision is open, stop and say so.
- **Tests first for anything involving money.** Write failing tests from the golden cases, then the implementation.
- Keep calculation code in pure functions with no database access, so it is easy to test.
- Stay inside the increment. Note ideas for other increments in the pull request instead of building them.
- **Definition of done:** tests pass, CI is green, migrations are included and reversible, the increment's row in `docs/PLAN.md` is updated, `docs/DECISIONS.md` is updated if a choice was made, and the pull request says what changed and what a reviewer should check.
- **Stop and ask** when a financial rule is ambiguous, a requirement conflicts with a hard rule, or the change needs to touch more than the increment's scope.

## Human review

A human reviews every pull request, and must review these closely: calculation engines, tenancy, authentication and roles, database migrations, the audit log, and anything touching money. Never merge your own pull request. Production deploys are manual and done by a human.

## Front-end conventions

- Use components from the design system. Do not restyle them locally.
- Never hardcode colors, spacing, or font sizes. Use the design tokens in `frontend/tokens/`. A lint rule enforces this.
- Every shared component has a Storybook story, including empty and loading states.
- Status is never shown by color alone. Use the shared status badge.
- The waterfall cascade component has two variants, payout (cool tones) and loss (warm tones), with an identical layout.

## Back-end conventions

- Python with type hints, formatted and linted with ruff, tested with pytest.
- Business logic lives in service modules, not in views or models.
- Every API write produces an audit entry.
- Permission checks follow the role matrix in `docs/ROLES.md`.
- Infrastructure stays portable to AWS: plain Dockerfiles, env-var config, no Railway-only features in code. Rules are in `docs/INFRASTRUCTURE.md`.

## Repo map

```
CLAUDE.md                  this file
docs/                      PLAN.md, DECISIONS.md, INFRASTRUCTURE.md, ROLES.md (to be written), design-handoff/
backend/                   Django project (has its own CLAUDE.md)
  config/settings/         base, dev, test, production settings
  config/urls.py           routes; /healthz is the liveness check
  tests/                   pytest suite
frontend/                  React app (has its own CLAUDE.md)
  tokens/                  design tokens, the only place colors, spacing, and type sizes live
  src/components/          shared design-system components
  src/screens/             one folder per screen
  eslint-rules/            local lint rules, including no-hardcoded-colors
golden-cases/              partner fixtures shared by back-end tests
.github/                   CI workflow and pull request template
docker-compose.yml         local stack; each service also has its own Dockerfile
.env.example               environment variable names, no values
```

## Glossary

- **Waterfall:** the priority order that decides which investor class is paid first from incoming cash.
- **Loss waterfall:** the order in which classes absorb losses; often the reverse of payout order.
- **Tier:** one step in a waterfall (return of principal, preferred return, catch-up, residual).
- **Ruleset:** a fund's versioned definition of its tiers. Versions are immutable once approved.
- **Run:** one execution of the waterfall for a period. Prepared by a maker, executed by a checker.
- **Settled:** cash has actually arrived, so it counts toward a run.
- **Servicer:** the provider that collects loan payments and reports events.
