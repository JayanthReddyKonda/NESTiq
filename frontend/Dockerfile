# ── Stage 1: build ────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Install deps
COPY package.json package-lock.json* ./
RUN npm install --prefer-offline

# Proxy target baked into vite.config.ts at build time.
# In Docker: http://backend:8000 (container DNS)
ARG VITE_PROXY_TARGET=http://localhost:8000
ENV VITE_PROXY_TARGET=$VITE_PROXY_TARGET

COPY . .
RUN npm run build

# ── Stage 2: serve ────────────────────────────────────────────────────────────
# Uses Vite's own preview server — no nginx, no extra deps.
# Port 4173 is Vite's preview default (configured in vite.config.ts).
FROM node:20-alpine AS serve

WORKDIR /app

# Only bring what the preview server needs
COPY --from=builder /app/dist        ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/vite.config.ts ./vite.config.ts

EXPOSE 4173

CMD ["npx", "vite", "preview", "--host", "0.0.0.0", "--port", "4173"]
