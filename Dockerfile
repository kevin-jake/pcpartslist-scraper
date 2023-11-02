# Stage 1: Build stage
# syntax=docker/dockerfile:1
FROM python:3.8-slim AS builder

# Set the working directory in the build stage
WORKDIR /app

# Install the required system packages for building Python packages and 'build-essential'
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV MYSQLCLIENT_CFLAGS="-I/usr/include/mysql"
ENV MYSQLCLIENT_LDFLAGS="-L/usr/lib/x86_64-linux-gnu -lmysqlclient"

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

WORKDIR /app/worker

# Set the command to run your application
# CMD ["ls"]
CMD ["celery", "-A", "tasks", "worker","--loglevel=info"]
