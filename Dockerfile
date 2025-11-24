FROM python:3.10-slim

WORKDIR /app

# Install dependencies system
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install deps langsung ke image
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
