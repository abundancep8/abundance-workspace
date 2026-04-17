FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend files
COPY jarvis/frontend/package.json jarvis/frontend/package-lock.json ./

# Install dependencies
RUN npm ci

# Copy source
COPY jarvis/frontend/src ./src
COPY jarvis/frontend/vite.config.js jarvis/frontend/index.html ./

# Build frontend
RUN npm run build

# Backend stage
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    espeak \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy backend
COPY jarvis/backend /app/backend

WORKDIR /app/backend

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy built frontend
COPY --from=frontend-builder /app/frontend/dist /app/backend/static

# Create necessary directories
RUN mkdir -p /home/user/.openclaw/workspace/{vault,memory}

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=info

# Expose ports
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Start server
CMD ["python", "server.py"]
