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
| `staging` (Railway) | Integration and demos | Automatic on merge to `main` | Seed data only |
| `production` | The live pilot | Manual, by a human only | Real tenant data; created in increment 1.9 |

## Staging on Railway

Project `cascadia`, workspace "Mikayla's Projects", region `sfo`.

| Service | Root directory | Watch paths | Restart policy | URL |
| --- | --- | --- | --- | --- |
| `backend` | `/backend` | `/backend/**` | On failure, 5 retries | https://backend-staging-bc95.up.railway.app |
| `frontend` | `/frontend` | `/frontend/**` | On failure, 5 retries | https://frontend-staging-5620.up.railway.app |
| `Postgres` | n/a | n/a | Platform managed | None; `postgres.railway.internal` only |

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

## Moving to AWS

A sketch, to be firmed up at the go-live review:

1. Create a VPC with private subnets for RDS and the ECS tasks, and public subnets for the load balancer.
2. Create RDS for PostgreSQL 18 with point-in-time recovery, and restore the latest dump into it.
3. Push both images to ECR from GitHub Actions, using the same Dockerfiles.
4. Run each image as an ECS Fargate service behind an Application Load Balancer, with health checks on `/healthz`.
5. Move every variable in the tables above into Secrets Manager or Parameter Store and inject them into the tasks.
6. Run migrations as a one-off ECS task (`RUN_MIGRATIONS=0` on the services).
7. Point DNS at the load balancer, then retire the Railway services.
