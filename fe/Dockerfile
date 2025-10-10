# ---------- Build stage ----------
FROM node:20-alpine AS builder
WORKDIR /app

# Install deps (lockfile-aware)
COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./
RUN \
  if [ -f package-lock.json ]; then npm ci --no-audit --no-fund; \
  elif [ -f pnpm-lock.yaml ]; then npm i -g pnpm && pnpm i --frozen-lockfile; \
  elif [ -f yarn.lock ]; then yarn install --frozen-lockfile; \
  else npm i --no-audit --no-fund; fi

# Build
COPY . .
# If you need backend URLs at build-time:
#   VITE_API_BASE="https://<backend-host>" VITE_WS_URL="wss://<backend-host>/ws" \
RUN npm run build

# ---------- Runtime (Nginx) ----------
FROM nginx:1.27-alpine
ENV PORT=8080

# SPA-friendly config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Static files
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 8080
#HEALTHCHECK CMD wget -qO- http://localhost:8080/health || exit 1

# No custom entrypoint — use nginx's default
CMD ["nginx", "-g", "daemon off;"]

