# Front-end image: builds the Vite app, then serves the static files with nginx on $PORT.
# Plain Docker on purpose, so it runs the same on Railway, docker compose, or AWS.
FROM node:22-alpine AS build

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .

# The SPA calls the API on relative /api URLs (same-origin; see
# nginx.conf.template). In local dev the Vite dev server proxies /api
# instead (vite.config.js).
RUN npm run build

FROM nginx:1.28-alpine

# The nginx image fills ${PORT} and ${BACKEND_URL} into templates at startup
# and leaves nginx variables alone.
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html

# BACKEND_URL is the API base URL the /api/ proxy forwards to. The default
# suits a same-host dev backend; every real deployment must override it
# (e.g. on Railway set BACKEND_URL=https://backend-uat.up.railway.app on the
# frontend service). It must never be empty: the rendered nginx config is
# invalid without a proxy target and the container will not start.
ENV BACKEND_URL="http://localhost:8000"
ENV PORT=8080
EXPOSE 8080
