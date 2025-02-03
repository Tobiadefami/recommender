# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry using the official installation script
RUN curl -sSL https://install.python-poetry.org | python3 -

# Ensure poetry is in the PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy the pyproject.toml and poetry.lock files to the container
COPY pyproject.toml poetry.lock /app/

# Disable virtualenv creation
RUN poetry config virtualenvs.create false

# Install the dependencies, updating the lock file if necessary
RUN poetry install --no-root

# Copy the rest of the application code to the container
COPY . /app/recommender

# Expose the port the app runs on
EXPOSE 8000

# Run app.py when the container launches
CMD ["poetry", "run", "uvicorn", "recommender.app:app", "--host", "0.0.0.0", "--port", "8000"]
