# syntax=docker/dockerfile:1
# Stage 1: Build stage
FROM python:3.8-slim AS builder

# Set the working directory in the build stage
WORKDIR /app

# Copy only the requirements file into the build stage
COPY requirements.txt /app/requirements.txt

# Install Python packages into a virtual environment to prevent conflicts
RUN python -m venv /app/venv
RUN /app/venv/bin/pip install --no-cache-dir -r /app/requirements.txt

# Stage 2: Final stage
FROM python:3.8-slim

# Copy the virtual environment with installed packages from the build stage
COPY --from=builder /app/venv /app/venv

# Set the PATH to include the virtual environment's bin directory
ENV PATH="/app/venv/bin:$PATH"

# Copy your application files into the container
COPY . /app

WORKDIR /app/server

# Set the command to run your application
CMD ["ls"]
# CMD ["celery", "-A", "tasks", "worker","--loglevel=info"]

# CMD [ "flask","--app", "api" "run"]