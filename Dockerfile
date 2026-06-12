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
COPY .env .

# Create persistent folders
RUN mkdir -p uploads mem0

# Expose Reflex ports
EXPOSE 3000
EXPOSE 8000

# Pre-compile the app to speed up container startup
RUN reflex export --frontend-only || true

CMD ["reflex", "run", "--env", "prod"]
