FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY agent/ ./agent/
COPY api/ ./api/

# Non-root user for security
RUN adduser --disabled-password --gecos "" appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
