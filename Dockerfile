# Stage 1: Build stage
# syntax=docker/dockerfile:1
FROM python:3.8-slim AS builder

# Install the required system packages for building Python packages and 'build-essential'
RUN apt-get update && apt-get install -y \
    build-essential \
    supervisor \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements file into the build stage
COPY requirements.txt /app/requirements.txt
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt
RUN playwright install
RUN playwright install-deps

# Copy your application files into the container
COPY . /app

WORKDIR /app

CMD ["/usr/bin/supervisord"]