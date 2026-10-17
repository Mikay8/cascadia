# Infrastructure

How Cascadia runs, and the rules that keep it portable. Railway hosts the build and the pilot; Cascadia may move to AWS later (see `DECISIONS.md`), so everything here is written to move without a rewrite.

## Portability rules

Every infrastructure change is checked against these. If one has to be broken, record why in `DECISIONS.md` first.

1. **Plain Dockerfiles are the only build.** Each service builds from its own `Dockerfile`. No Railpack, Nixpacks, buildpacks, or platform build commands.
2. **All configuration is environment variables.** Code reads settings from the environment; the variable names are listed in `.env.example`. No platform SDKs or platform-only config files in the code.
3. **Standard PostgreSQL only.** Connect with `DATABASE_URL`. No platform database extensions or proprietary features.
4. **Listen on `$PORT` and answer `/healthz`.** Every service does both, so any load balancer or orchestrator can run it.
5. **Logs go to stdout and stderr.** No platform logging agents in the code.
6. **No state on the container disk.** Files that must persist go to the database or, later, S3-compatible object storage.
7. **Platform settings are written down here.** Anything set in a dashboard (root directory, health check path, watch paths, domains) is recorded below, so it can be recreated elsewhere.

Railway-only conveniences we use, and what replaces them on AWS:

| Railway feature | Why we use it | Replacement on AWS |
| --- | --- | --- |
| Reference variables (`${{Postgres.DATABASE_URL}}`) | Wires the database URL into the back end | Secrets Manager or SSM Parameter Store, injected into the ECS task |
| Private networking (`*.railway.internal`) | The database is never public | A private VPC subnet with security groups |
| Generated domains (`*.up.railway.app`) | Staging URLs without DNS setup | Route 53 with an Application Load Balancer and ACM certificates |
| Deploy on push from GitHub | Staging deploys on merge to `main` | GitHub Actions pushing images to ECR, then updating the ECS service |
| Managed Postgres template | Quick database for staging | RDS for PostgreSQL 18 |

## Services

| Service | Source | Image | Port | Health check | Public |
| --- | --- | --- | --- | --- | --- |
| `backend` | `backend/Dockerfile` | Python 3.12, Django, gunicorn | `$PORT` (8000) | `GET /healthz` | Yes, HTTPS only |
| `frontend` | `frontend/Dockerfile` | Vite build served by nginx | `$PORT` (8080) | `GET /healthz` | Yes, HTTPS only |
| `Postgres` | Railway Postgres template | PostgreSQL 18 | 5432 | Platform managed | No, private network only |

The back end runs migrations on start (`RUN_MIGRATIONS=1`). With more than one replica, or on AWS, set `RUN_MIGRATIONS=0` and run `python manage.py migrate` as a separate release step before the new version starts.

## Environments

| Environment | Purpose | Deploys | Data |
| --- | --- | --- | --- |
| Local (`docker compose up`) | Development | On save | Seed data only |
| `staging` (Railway) | Legacy; proposed for retirement once UAT is verified | Pinned to branch `1.1-docker-staging` (behind `main`) | Seed data only |
| `uat` (Railway) | Pre-prod gate: preview increments before they reach `main` | Automatic on push to the `uat` branch | Seed data only |
| `production` (Railway) | The live pilot (sandbox until increment 1.9 hardens it) | Manual, by a human only, from `main` | Seed data only; real tenant data after 1.9 |

Branch flow (decided 2026-10-17): feature PRs target the long-lived `uat` branch; UAT auto-deploys from it. Promote `uat` → `main` via PR when the increment is accepted; production deploys from `main` manually.

## Railway environments

Project `cascadia`, workspace "Mikayla's Projects", region `us-west` (SFO).

| Environment | Service | Branch | Auto-deploy | URL |
| --- | --- | --- | --- | --- |
| `staging` | `backend` | `1.1-docker-staging` | On | https://backend-staging-bc95.up.railway.app |
| `staging` | `frontend` | `1.1-docker-staging` | On | https://frontend-staging-5620.up.railway.app |
| `staging` | `Postgres` | n/a (template) | n/a | None; `postgres.railway.internal` only |
| `uat` | `backend` | `uat` | On (push to `uat`) | https://backend-uat.up.railway.app |
| `uat` | `frontend` | `uat` | On (push to `uat`) | https://frontend-uat.up.railway.app |
| `uat` | `Postgres` | n/a (template) | n/a | None; `postgres.railway.internal` only |
| `production` | `backend` | `main` | Off (manual only) | https://backend-production-4aa2.up.railway.app |
| `production` | `frontend` | `main` | Off (manual only) | https://frontend-production-fb46.up.railway.app |
| `production` | `Postgres` | n/a (template) | n/a | None; `postgres.railway.internal` only |

Root directory, watch paths, and restart policy per service are as before (`/backend` and `/frontend` roots, watch `/backend/**` and `/frontend/**`, restart on failure with 5 retries).

Back-end variables (values live in Railway, never in the repo):

| Variable | Staging value |
| --- | --- |
| `DJANGO_SETTINGS_MODULE` | `config.settings.production` |
| `DJANGO_SECRET_KEY` | Random, set in Railway. Rotate from the dashboard. |
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` (private network) |
| `DJANGO_ALLOWED_HOSTS` | The back-end domain, plus `healthcheck.railway.app` for Railway's health check |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://` plus the back-end domain |
| `PORT`, `WEB_CONCURRENCY`, `RUN_MIGRATIONS` | `8000`, `2`, `1` |

Front-end variables: `PORT` is `8080`. The front end has no secrets.

Create services one at a time on Railway. Creating two at once left both stuck in "applying" and had to be cleared by hand in the dashboard.

## Secrets

- Never commit a secret, and never put real data in staging (hard rule 8).
- Secrets are set in the platform's secret store: Railway variables today, AWS Secrets Manager later.
- Production secrets are created and entered by a human, not by an AI session.
- The `production` environment was duplicated from `staging`, so its `DJANGO_SECRET_KEY` is currently a copy of staging's. Rotate it from the Railway dashboard before any real data or real users touch production.

## Moving to AWS

A sketch, to be firmed up at the go-live review:

1. Create a VPC with private subnets for RDS and the ECS tasks, and public subnets for the load balancer.
2. Create RDS for PostgreSQL 18 with point-in-time recovery, and restore the latest dump into it.
3. Push both images to ECR from GitHub Actions, using the same Dockerfiles.
4. Run each image as an ECS Fargate service behind an Application Load Balancer, with health checks on `/healthz`.
5. Move every variable in the tables above into Secrets Manager or Parameter Store and inject them into the tasks.
6. Run migrations as a one-off ECS task (`RUN_MIGRATIONS=0` on the services).
7. Point DNS at the load balancer, then retire the Railway services.
