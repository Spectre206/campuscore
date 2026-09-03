# Use Python 3.12 slim as base
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies needed for psycopg and build
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    build-essential \
    postgresql-client \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*
    
# Create and set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . /app/

# Copy entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Run entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command (can be overridden in compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]