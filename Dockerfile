# IgnisBot Dockerfile
# Multi-stage build for optimized image size

FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 ignisbot && \
    mkdir -p /app/logs && \
    chown -R ignisbot:ignisbot /app

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/ignisbot/.local

# Copy application files
# Copy everything except what's in .dockerignore
COPY --chown=ignisbot:ignisbot . .

# Verify files were copied (debug step - will show in build logs)
# This runs AFTER copying, so we can verify what was actually copied
RUN ls -la /app/ && \
    echo "--- Contents of /app/utils/ ---" && \
    ls -la /app/utils/ && \
    echo "--- Checking for required files ---" && \
    test -f /app/utils/config.py && echo "✓ utils/config.py exists" || echo "✗ utils/config.py MISSING" && \
    test -f /app/utils/__init__.py && echo "✓ utils/__init__.py exists" || echo "✗ utils/__init__.py MISSING" && \
    test -f /app/ignis_main.py && echo "✓ ignis_main.py exists" || echo "✗ ignis_main.py MISSING" && \
    echo "--- Python path test ---" && \
    python -c "import sys; print('PYTHONPATH:', sys.path)" && \
    python -c "import os; print('Current dir:', os.getcwd()); print('Files in /app:', os.listdir('/app'))"

# Switch to non-root user
USER ignisbot

# Add local bin to PATH and set PYTHONPATH
ENV PATH=/home/ignisbot/.local/bin:$PATH
ENV PYTHONPATH=/app:$PYTHONPATH
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "ignis_main.py"]

