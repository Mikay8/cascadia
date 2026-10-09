#!/bin/sh
# Container entrypoint. Runs migrations, then serves the API with gunicorn on $PORT.
#
# Set RUN_MIGRATIONS=0 when migrations run as a separate release step instead (for example an
# ECS one-off task on AWS, or once there is more than one replica).
set -e

if [ "${RUN_MIGRATIONS:-1}" = "1" ]; then
  python manage.py migrate --noinput
fi

exec gunicorn config.wsgi \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers "${WEB_CONCURRENCY:-2}" \
  --access-logfile - \
  --error-logfile /dev/stdout \
  --forwarded-allow-ips "*"
