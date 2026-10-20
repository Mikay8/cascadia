# Front-end image: builds the Vite app, then serves the static files with nginx on $PORT.
# Plain Docker on purpose, so it runs the same on Railway, docker compose, or AWS.
FROM node:22-alpine AS build

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .

# The SPA calls the API on relative /api URLs, proxied by nginx (see
# nginx.conf.template) so the app is same-origin: cookies are first-party and
# no CORS dance is needed. BACKEND_URL is the API's base URL and is required
# in any environment that serves this image (e.g. on Railway set
# BACKEND_URL=https://backend-uat.up.railway.app on the frontend service).
# In local dev the Vite dev server proxies /api instead (vite.config.js).
ENV BACKEND_URL=""
RUN npm run build

FROM nginx:1.28-alpine

# The nginx image fills ${PORT} into templates at startup and leaves nginx variables alone.
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html

ENV PORT=8080
EXPOSE 8080
