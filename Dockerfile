# Base image
FROM python:3.9-slim

# Set environment variables to avoid Python writing .pyc files and buffering output
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV DOCKER=True

# Install git
RUN apt-get update && \
    apt-get install -y \
    git \
    && apt-get clean

# Set workdir and copy the source code
RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/
COPY app/ /app/
RUN mkdir /app/repos

# Create a Python virtual environment inside the container and install dependencies
RUN python3 -m venv /venv \
    && /venv/bin/pip install --upgrade pip \
    && /venv/bin/pip install -r requirements.txt

# Expose port for gunicorn
EXPOSE 5000

CMD ["/venv/bin/gunicorn"]
