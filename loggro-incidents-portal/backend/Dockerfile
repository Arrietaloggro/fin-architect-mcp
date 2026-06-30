# ── Stage 1: Build ────────────────────────────────────────────────────────────
FROM node:20-slim AS builder

# Build tools required by better-sqlite3 (native C++ addon)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 make g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install deps (cache bust only when package files change)
COPY package.json package-lock.json ./
RUN npm ci --cache /tmp/.npm

# Build TypeScript
COPY tsconfig.json ./
COPY src/ ./src/
RUN npm run build

# Remove devDependencies (keeps compiled native addons intact)
RUN npm prune --omit=dev

# ── Stage 2: Production ───────────────────────────────────────────────────────
FROM node:20-slim

WORKDIR /app

# Copy pruned node_modules (includes compiled better-sqlite3 .node binary)
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
COPY package.json ./

ENV NODE_ENV=production

# Railway injects $PORT automatically
EXPOSE 3001

CMD ["node", "dist/server.js"]
