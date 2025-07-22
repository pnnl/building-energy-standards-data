FROM mcr.microsoft.com/devcontainers/python:3.10

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Confirm it's installed
RUN /usr/local/bin/poetry --version

# Set working directory
WORKDIR /workspace

# Install Python dependencies
COPY pyproject.toml poetry.lock ./
# RUN poetry install

# Default command removed for devcontainer compatibility