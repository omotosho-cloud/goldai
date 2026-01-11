FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with timeout and retries
RUN pip install --no-cache-dir --timeout=1000 --retries=5 -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p static/css static/js templates

# Expose port (Railway uses PORT env variable)
EXPOSE $PORT

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/api/status || exit 1

# Run the application
CMD ["python", "app.py"]