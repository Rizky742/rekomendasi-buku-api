FROM python:3.10-slim

WORKDIR /app

# Install dependencies system
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Create venv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install deps
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy all source code
COPY . .

COPY data ./data

# Gunicorn command
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
