# 1. Use an official lightweight Python image
FROM python:3.12-slim

# 2. Set environment variables to prevent Python from buffering logs
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Set work directory
WORKDIR /app

# 4. Install system dependencies for Postgres and general tools
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 5. Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the entire project code
COPY . .

# 7. Create a directory for logs (as per your previous requirement)
RUN mkdir -p /app/logs

# 8. Expose the port Django runs on
EXPOSE 8000