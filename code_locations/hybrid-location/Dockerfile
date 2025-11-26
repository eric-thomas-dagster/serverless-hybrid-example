# Dockerfile for Dagster+ Hybrid Location
FROM python:3.12-slim

# Install uv for fast dependency installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY src/ ./src/

# Install dependencies using uv
RUN uv pip install --system --no-cache -e .

# Set the Dagster home directory
ENV DAGSTER_HOME=/app/dagster_home

# No ENTRYPOINT - Dagster Cloud agent provides the full command
