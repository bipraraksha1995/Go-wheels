FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Run security checks
RUN bandit -r gowheels/ -ll || true
RUN safety check || true

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Run tests
RUN python manage.py test tests || true

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
