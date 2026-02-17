FROM python:3.11-slim

# Install system dependencies for PostGIS/GeoAlchemy and backup
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create directory for backups and media
RUN mkdir -p /app/backups /app/media

CMD ["python", "bot.py"]
