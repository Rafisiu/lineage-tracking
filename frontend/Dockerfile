# Frontend Dockerfile
# Note: Build this from the project root with: docker build -f frontend/Dockerfile .
FROM node:20-alpine AS builder

WORKDIR /app

# Copy root workspace package files
COPY package.json ./
COPY package-lock.json* ./

# Copy frontend package files
COPY frontend/package.json ./frontend/

# Install dependencies (generates package-lock.json if missing, then installs)
RUN if [ ! -f package-lock.json ]; then npm install; else npm ci; fi

# Copy frontend source code
COPY frontend ./frontend/

# Build the frontend application
WORKDIR /app/frontend
RUN npm run build

# Production stage with nginx
FROM nginx:alpine

# Copy built assets from builder stage
COPY --from=builder /app/frontend/dist /usr/share/nginx/html

# Copy nginx configuration
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Create non-root user and set permissions
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid

USER nginx

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
