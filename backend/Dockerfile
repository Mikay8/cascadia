# Django API image. Plain Docker on purpose: the same image runs on Railway, docker compose,
# or AWS ECS. All configuration comes from environment variables (see .env.example).
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN useradd --create-home --uid 1000 app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Static files are collected at build time. The values below exist only so production settings
# load; collectstatic never connects to the database or uses the key.
RUN DJANGO_SETTINGS_MODULE=config.settings.production \
    DJANGO_SECRET_KEY=build-only \
    DATABASE_URL=postgres://build:build@localhost:5432/build \
    DJANGO_ALLOWED_HOSTS=build \
    python manage.py collectstatic --noinput

USER app

ENV DJANGO_SETTINGS_MODULE=config.settings.production \
    PORT=8000
EXPOSE 8000

CMD ["sh", "start.sh"]
