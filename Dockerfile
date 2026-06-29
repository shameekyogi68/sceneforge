# syntax=docker/dockerfile:1
FROM python:3.11.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Reflex FNM requires curl and unzip to install node automatically
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc curl unzip \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source folders
COPY backend/ ./backend/
COPY sceneforge/ ./sceneforge/
COPY rxconfig.py .

# Create persistent folders
RUN mkdir -p uploads mem0

# Run as a non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && chown -R appuser:appuser /app
USER appuser

# Expose Reflex ports
EXPOSE 3000
EXPOSE 8000

# The production API_URL must be passed at build time so the static frontend
# bakes the correct WebSocket/HTTP backend host. In Reflex Cloud / single-origin
# deployments this should be the public origin of the app.
ARG API_URL
ENV API_URL=${API_URL}
RUN if [ -z "$API_URL" ]; then echo "WARNING: API_URL is not set; frontend will default to localhost."; fi
RUN reflex export --frontend-only

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["reflex", "run", "--env", "prod"]
