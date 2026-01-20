# 1. Use an official lightweight Python image
FROM python:3.12-slim

# 2. Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Set work directory
WORKDIR /app

# 4. Install system dependencies (UPDATED FOR PYGRAPHVIZ)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    curl \
    graphviz \
    graphviz-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 5. Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of the code
COPY . .

# 7. Create logs directory
RUN mkdir -p /app/logs

EXPOSE 8000