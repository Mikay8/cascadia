# Front-end image: builds the Vite app, then serves the static files with nginx on $PORT.
# Plain Docker on purpose, so it runs the same on Railway, docker compose, or AWS.
FROM node:22-alpine AS build

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .

# Baked into the bundle at build time; Railway injects it per environment
# (e.g. VITE_API_URL=https://backend-uat.up.railway.app).
ARG VITE_API_URL=""
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

FROM nginx:1.28-alpine

# The nginx image fills ${PORT} into templates at startup and leaves nginx variables alone.
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html

ENV PORT=8080
EXPOSE 8080
