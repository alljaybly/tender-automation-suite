FROM python:3.11-slim

# Install system packages
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy everything
COPY . /app

# Create all required directories
RUN mkdir -p /app/templates /app/static \
    /app/workspace/uploads \
    /app/workspace/outputs \
    /app/workspace/history \
    /app/workspace/merged

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
