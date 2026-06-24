FROM python:3.11-slim
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

# Expose Reflex ports
EXPOSE 3000
EXPOSE 8000

# Pre-compile the frontend with the correct production API URL so env.json
# bakes in the right WebSocket/HTTP backend host instead of localhost.
# Without this, the browser gets a stale or localhost URL and the WebSocket
# connection is rejected with a 403.
ARG API_URL=https://b2d09cec-8f73-4370-b726-2907b4163a38.fly.dev
ENV API_URL=${API_URL}
RUN reflex export --frontend-only || true

CMD ["reflex", "run", "--env", "prod"]
