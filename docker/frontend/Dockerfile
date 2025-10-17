# ---- Base Stage ----
FROM node:22-alpine AS base

WORKDIR /app/frontend

# Copy package files
COPY ./frontend/package*.json ./

# ---- Dependencies Stage ----
FROM base AS dependencies

# Install all dependencies (including devDependencies for build)
RUN npm ci

# ---- Development Stage ----
FROM base AS development

# Install all dependencies
RUN npm ci

# Copy source code
COPY ./frontend ./

# Expose Vite dev server port
EXPOSE 5173

# Run Vite dev server with hot-reload
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# ---- Build Stage ----
FROM dependencies AS build

# Copy source code
COPY ./frontend ./

# Build the application
RUN npm run build

# ---- Production Stage ----
FROM nginx:1.27-alpine AS production

# Copy custom nginx config if needed
COPY docker/frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Copy built files from build stage
COPY --from=build /app/frontend/dist /usr/share/nginx/html

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:80/ || exit 1

# Create non-root user for nginx
RUN addgroup -g 101 -S nginx && \
    adduser -S -D -H -u 101 -h /var/cache/nginx -s /sbin/nologin -G nginx -g nginx nginx 2>/dev/null || true

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]