FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system packages required for building some Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    g++ \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY app/requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire application folder
COPY app /app/app

# Make PYTHONPATH point to project root (/app)
ENV PYTHONPATH=/app

# Expose FastAPI port
EXPOSE 8000

# Default command (web service)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
