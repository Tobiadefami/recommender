# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv

COPY --from=ghcr.io/astral-sh/uv:0.10.5 /uv /uvx /bin/

# Copy dependency metadata first to keep Docker layer caching effective
COPY pyproject.toml uv.lock /app/

# Install locked dependencies
RUN uv sync --locked --no-dev

# Copy the rest of the application code to the container
COPY recommender /app/recommender

# Expose the port the app runs on
EXPOSE 8000

# Run app.py when the container launches
CMD ["uv", "run", "--locked", "--no-dev", "uvicorn", "recommender.app:app", "--host", "0.0.0.0", "--port", "8000"]
