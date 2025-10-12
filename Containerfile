# NeoBank & Chrome Slots - OCI-Compliant Container Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (including PostgreSQL client libraries and curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY init_db.py .
COPY scripts/ ./scripts/

# Make scripts executable
RUN chmod +x /app/scripts/*.sh /app/scripts/*.py

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=backend/app.py

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Set Python path so backend package is importable
ENV PYTHONPATH=/app

# Use entrypoint script
ENTRYPOINT ["/app/scripts/entrypoint.sh"]

# Run application with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "backend.app:app"]
