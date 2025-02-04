# Dockerfile
# Build stage
FROM python:3.10-slim-bullseye as builder

WORKDIR /app
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY scripts/requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.10-slim-bullseye

WORKDIR /app
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.local/bin:${PATH}"

# Copy built artifacts
COPY --from=builder /root/.local /root/.local
COPY --chown=1001:1001 . .

# Create non-root user
RUN groupadd -r botuser && useradd -r -g botuser -u 1001 botuser \
    && chown -R botuser:botuser /app/data

USER botuser

# Healthcheck configuration
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python scripts/deploy/healthcheck.py

# Runtime command
CMD ["python", "-m", "bot.bot"]